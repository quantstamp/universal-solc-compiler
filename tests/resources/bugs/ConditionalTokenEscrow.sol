/***************************************************************************************************
 *                                                                                                 *
 * (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,         *
 * modified, redistributed, or otherwise disseminated except to the extent expressly authorized by *
 * Quantstamp for credentialed users. This content and its use are governed by the Quantstamp      *
 * Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.     *
 *                                                                                                 *
 **************************************************************************************************/

pragma solidity ^0.4.24;

import "./TokenEscrowMock.sol";

/**
 * @title ConditionalTokenEscrow
 * @dev Base abstract escrow to only allow withdrawal of tokens
 * if a condition is met.
 */
contract ConditionalTokenEscrow is TokenEscrowMock {
  /**
  * @dev Returns whether an address is allowed to withdraw their tokens.
  * To be implemented by derived contracts.
  * @param _payee The destination address of the tokens.
  */
  function withdrawalAllowed(address _payee) public view returns (bool);

  function withdraw(address _payee) public {
    require(withdrawalAllowed(_payee));
    super.withdraw(_payee);
  }
}
