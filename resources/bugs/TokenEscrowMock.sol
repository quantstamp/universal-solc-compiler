/***************************************************************************************************
 *                                                                                                 *
 * (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,         *
 * modified, redistributed, or otherwise disseminated except to the extent expressly authorized by *
 * Quantstamp for credentialed users. This content and its use are governed by the Quantstamp      *
 * Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.     *
 *                                                                                                 *
 **************************************************************************************************/

/**
 * NOTE: All contracts in this directory were taken from a non-master branch of openzeppelin-solidity.
 * This contract was modified to be a whitelist.
 * Commit: ed451a8688d1fa7c927b27cec299a9726667d9b1
 */

pragma solidity ^0.4.24;

/**
 * @title SafeMath
 * @dev Math operations with safety checks that revert on error
 */
library SafeMath {

  /**
  * @dev Multiplies two numbers, reverts on overflow.
  */
  function mul(uint256 a, uint256 b) internal pure returns (uint256) {
    // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
    // benefit is lost if 'b' is also tested.
    // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
    if (a == 0) {
      return 0;
    }

    uint256 c = a * b;
    require(c / a == b);

    return c;
  }

  /**
  * @dev Integer division of two numbers truncating the quotient, reverts on division by zero.
  */
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b > 0); // Solidity only automatically asserts when dividing by 0
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold

    return c;
  }

  /**
  * @dev Subtracts two numbers, reverts on overflow (i.e. if subtrahend is greater than minuend).
  */
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b <= a);
    uint256 c = a - b;

    return c;
  }

  /**
  * @dev Adds two numbers, reverts on overflow.
  */
  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    require(c >= a);

    return c;
  }

  /**
  * @dev Divides two numbers and returns the remainder (unsigned integer modulo),
  * reverts when dividing by zero.
  */
  function mod(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b != 0);
    return a % b;
  }
}

/**
 * @title TokenEscrow
 * @dev Holds tokens destinated to a payee until they withdraw them.
 * The contract that uses the TokenEscrow as its payment method
 * should be its owner, and provide public methods redirecting
 * to the TokenEscrow's deposit and withdraw.
 * Moreover, the TokenEscrow should also be allowed to transfer
 * tokens from the payer to itself.
 */
contract TokenEscrowMock {
  using SafeMath for uint256;

  event Deposited(address indexed payee, uint256 tokenAmount);
  event Withdrawn(address indexed payee, uint256 tokenAmount);

  mapping(address => uint256) private deposits;

  // changing ERC20 to general address, this contact skips token manipulation
  address public token;

  // changing ERC20 to general address, this contact skips token manipulation
  constructor (address _token) public {
    require(_token != address(0));
    token = _token;
  }

  function depositsOf(address _payee) public view returns (uint256) {
    return deposits[_payee];
  }

  // removed only whitelisted
  /**
  * @dev Puts in escrow a certain amount of tokens as credit to be withdrawn.
  * @param _payee The destination address of the tokens.
  * @param _amount The amount of tokens to deposit in escrow.
  */
  function deposit(address _payee, uint256 _amount) public {
    deposits[_payee] = deposits[_payee].add(_amount);

    // the implementation contains the following transfer, the mock will skip it
    // token.safeTransferFrom(msg.sender, address(this), _amount);

    emit Deposited(_payee, _amount);
  }

  // removed only whitelisted
  /**
  * @dev Withdraw accumulated tokens for a payee.
  * @param _payee The address whose tokens will be withdrawn and transferred to.
  */
  function withdraw(address _payee) public {
    uint256 payment = deposits[_payee];

    // the implementation contains the following assertion, the mock will skip it
    // assert(token.balanceOf(address(this)) >= payment);

    deposits[_payee] = 0;

    // the implementation contains the following transfer, the mock will skip it
    // token.safeTransfer(_payee, payment);

    emit Withdrawn(_payee, payment);
  }
}
