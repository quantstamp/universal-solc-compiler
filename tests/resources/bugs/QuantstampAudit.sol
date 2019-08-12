/***************************************************************************************************
 *                                                                                                 *
 * (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,         *
 * modified, redistributed, or otherwise disseminated except to the extent expressly authorized by *
 * Quantstamp for credentialed users. This content and its use are governed by the Quantstamp      *
 * Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.     *
 *                                                                                                 *
 **************************************************************************************************/

pragma solidity ^0.4.18;

import "./Queue.sol";

contract QuantstampAuditInternal {

  // state of audit requests submitted to the contract
  // TODO: code clone
  enum AuditState {
    None,
    Pending,
    Queued,
    Assigned,
    Completed,  // automated audit finished successfully and the report is available
    Error,      // automated audit failed to finish; the report contains detailed information about the error
    Timeout     // automated audit timed out, as no auditor node returned the report
  }

  /**
    * @dev AuditRequest contains the requestor address, the request uri, and the price
    */
  struct AuditRequest {
    address requestor;
    string uri;
    uint256 price;
    AuditState state;
    address auditor;
    uint requestBlockNumber;
  }

  /**
    * @dev Audit report contains the auditor address and the actual report
    */
  struct AuditReport {
    uint256 requestId;
    address auditor;
    string reportHash;
  }

  // keeps track of audit requests
  mapping(uint256 => AuditRequest) private auditRequests;
  // keeps track of audit reports
  mapping(uint256 => AuditReport) private auditReports;

  // TODO: figure out what a reasonable value for timeout is. For now 10 blocks.
  uint public auditTimeoutInBlocks = 10;

  event LogAuditQueued(uint256 requestId, address requestor, string uri, uint256 price);
  event LogAuditRequestAssigned(uint256 requestId, address auditor, address requestor, string uri, uint256 price);
  event LogReportSubmitted(uint256 requestId, address auditor, AuditState auditResult, string reportHash);
  event LogAuditAlreadyExists(uint256 requestId);
  event LogReportSubmissionError_InvalidAuditor(uint256 requestId, address auditor);
  event LogReportSubmissionError_InvalidState(uint256 requestId, AuditState state);
  event LogErrorAlreadyAudited(uint256 requestId, address requestor, string uri);
  event LogUnableToQueueAudit(uint256 requestId, address requestor, string uri);
  event LogUnableToAssignAudit(uint256 requestId);
  event LogAuditQueueIsEmpty();

  Uint256Queue requestQueue;
  Uint256Queue assignedQueue;
  uint constant REQUEST_QUEUE_CAPACITY = 30000;

  function QuantstampAuditInternal() public {
    requestQueue = new Uint256Queue(REQUEST_QUEUE_CAPACITY);
    assignedQueue = new Uint256Queue(REQUEST_QUEUE_CAPACITY);
  }

  function queueAudit(uint256 requestId, address requestor, string uri, uint256 price) public {
    if (auditRequests[requestId].state != AuditState.None) {
      LogAuditAlreadyExists(requestId);
      return;
    }

    if (requestQueue.push(requestId) != Uint256Queue.PushResult.Success) {
      LogUnableToQueueAudit(requestId, requestor, uri);
      return;
    }
    auditRequests[requestId] = AuditRequest(requestor, uri, price, AuditState.Queued, address(0), block.number);
    LogAuditQueued(requestId, requestor, uri, price);
  }

  function getNextAuditRequest() public {
    Uint256Queue.PopResult popResult;
    uint256 requestId;

    (popResult, requestId) = requestQueue.pop();
    if (popResult == Uint256Queue.PopResult.QueueIsEmpty) {
      LogAuditQueueIsEmpty();
      return;
    }
    if (assignedQueue.push(requestId) != Uint256Queue.PushResult.Success) {
      LogUnableToAssignAudit(requestId);
      return;
    }
    auditRequests[requestId].state = AuditState.Assigned;
    auditRequests[requestId].auditor = msg.sender;
    auditRequests[requestId].requestBlockNumber = block.number;

    LogAuditRequestAssigned(
      requestId,
      auditRequests[requestId].auditor,
      auditRequests[requestId].requestor,
      auditRequests[requestId].uri,
      auditRequests[requestId].price
    );
  }

  function submitReport(uint256 requestId, AuditState auditResult, string reportHash) public {
    AuditRequest storage request = auditRequests[requestId];
    if (request.state != AuditState.Assigned && request.state != AuditState.Timeout) {
      LogReportSubmissionError_InvalidState(requestId, request.state);
      return;
    }

    // the sender must be the auditor
    if (msg.sender != request.auditor)  {
      LogReportSubmissionError_InvalidAuditor(requestId, msg.sender);
      return;
    }

    // if the analysis timeouts, the auditor address is set to 0
    address auditor = auditResult == AuditState.Timeout ? address(0) : msg.sender;
    auditReports[requestId] = AuditReport(requestId, auditor, reportHash);
    request.state = auditResult;
    LogReportSubmitted(requestId, auditor, auditResult, reportHash);
  }

  function getAuditState(uint256 requestId) public constant returns(AuditState) {
    return auditRequests[requestId].state;
  }

  function getQueueLength() public constant returns(uint) {
    return requestQueue.length();
  }

  function getQueueCapacity() public constant returns(uint) {
    return requestQueue.capacity();
  }

  function setAuditTimeout(uint timeoutInBlocks) public {
    auditTimeoutInBlocks = timeoutInBlocks;
  }

  // Loops over front audits in the assigned queue to detect timeouts. If an audit is finished, removes it from the queue.
  function detectAuditTimeouts() public {
    Uint256Queue.PopResult popResult;
    uint256 requestId;

    // loops over the queue while not empty
    while(!assignedQueue.isEmpty()) {
      // looks at the front of the queue
      (popResult, requestId) = assignedQueue.peek();
      detectTimeout(requestId);
      // if the audit at the front is still pending, return
      if (!isFinished(requestId)) {
        return;
      }
      // otherwise, remove the element and keep looping
      assignedQueue.pop();
    }
  }

  /**
   * @dev Detects if a given audit request timed out. If so, it sets requests' status to timeout and submits the report.
   * @param requestId Unique ID of the audit request.
   */
  function detectTimeout(uint256 requestId) public {
    AuditRequest storage audit = auditRequests[requestId];

    // conditions for detecting a timeout
    if (audit.state == AuditState.Timeout ||
      (audit.requestBlockNumber + auditTimeoutInBlocks) < block.number) {
      // updates the status
      audit.state = AuditState.Timeout;
      audit.auditor = msg.sender;
      // submits a report for timeout
      submitReport(requestId, AuditState.Timeout, "");
    }
  }

  /**
   * @dev Returns funds to the requestor.
   * @param requestId Unique ID of the audit request.
   */
  // TODO: code clone
  function isFinished(uint256 requestId) view public returns(bool) {
    return auditRequests[requestId].state == AuditState.Completed
      || auditRequests[requestId].state == AuditState.Error
      || auditRequests[requestId].state == AuditState.Timeout;
  }
}
