/***************************************************************************************************
 *                                                                                                 *
 * (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,         *
 * modified, redistributed, or otherwise disseminated except to the extent expressly authorized by *
 * Quantstamp for credentialed users. This content and its use are governed by the Quantstamp      *
 * Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.     *
 *                                                                                                 *
 **************************************************************************************************/

pragma solidity ^0.4.2;

contract SendBalance {
  mapping (address => uint) userBalances;
  bool withdrawn = false;

  function getBalance(address u) constant returns (uint) {
    return userBalances[u];
  }

  function addToBalance() {
    userBalances[msg.sender] += msg.value;
  }

  function withdrawBalance() {
    if (!(msg.sender.call.value(userBalances[msg.sender])())) {
      throw;
    }

    userBalances[msg.sender] = 0;
  }
}
