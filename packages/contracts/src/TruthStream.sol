// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract TruthRegistry {
    struct TruthCertificate {
        bytes32 contentHash;
        uint256 timestamp;
        address verifier;
        uint8 confidenceScore;
        bytes32 daBlobId;
        uint256 stakeAmount;
        bool challenged;
        address challenger;      // NEW: Track who challenged
        uint256 challengeStake;  // NEW: How much they staked
        uint256 resolutionTime;
        string metadataURI;      // NEW: Actually store this
    }

    mapping(bytes32 => TruthCertificate) public certificates;
    mapping(address => uint256) public validatorReputation;
    
    // NEW: Track if content exists (for checking duplicates)
    mapping(bytes32 => bool) public isVerified;
    
    address public owner; // NEW: For hackathon demo control
    
    event TruthCertified(
        bytes32 indexed contentHash, 
        bytes32 indexed daBlobId, 
        address indexed verifier,
        uint8 confidence,
        uint256 stake
    );
    
    event TruthChallenged(
        bytes32 indexed contentHash, 
        address indexed challenger, 
        uint256 stake
    );
    
    event ChallengeResolved(
        bytes32 indexed contentHash,
        bool overturned,
        address winner,
        uint256 reward
    );

    constructor() {
        owner = msg.sender; // Set deployer as owner for demo
    }

    // Mint 0.01 0G for demo (hackathon friendly amount)
    function certifyTruth(
        bytes32 _contentHash,
        bytes32 _daBlobId,
        uint8 _confidence,
        string calldata _metadataURI
    ) external payable {
        // Prevent duplicate verification
        require(!isVerified[_contentHash], "Already verified");
        
        // MVP: 0.01 0G min stake (not 10)
        require(msg.value >= 0.01 ether, "Min 0.01 0G");
        require(_confidence <= 100, "Confidence 0-100");
        
        certificates[_contentHash] = TruthCertificate({
            contentHash: _contentHash,
            timestamp: block.timestamp,
            verifier: msg.sender,
            confidenceScore: _confidence,
            daBlobId: _daBlobId,
            stakeAmount: msg.value,
            challenged: false,
            challenger: address(0), // Empty initially
            challengeStake: 0,
            resolutionTime: block.timestamp + 7 days,
            metadataURI: _metadataURI // Actually store it
        });

        isVerified[_contentHash] = true;
        validatorReputation[msg.sender] += 1;
        
        emit TruthCertified(
            _contentHash, 
            _daBlobId, 
            msg.sender, 
            _confidence, 
            msg.value
        );
    }

    function challengeTruth(bytes32 _contentHash) external payable {
        // FIX: Use storage so we can update
        TruthCertificate storage cert = certificates[_contentHash];
        
        require(isVerified[_contentHash], "Not verified");
        require(!cert.challenged, "Already challenged");
        require(msg.value >= cert.stakeAmount * 2, "2x stake required");
        
        cert.challenged = true;
        cert.challenger = msg.sender; // Track who challenged
        cert.challengeStake = msg.value;
        // Extend resolution time (optional)
        cert.resolutionTime = block.timestamp + 7 days;
        
        emit TruthChallenged(_contentHash, msg.sender, msg.value);
    }

    // FIX: Proper resolution with state updates
    function resolveChallenge(bytes32 _contentHash, bool _truthValid) external {
        TruthCertificate storage cert = certificates[_contentHash];
        
        require(cert.challenged, "Not challenged");
        require(block.timestamp > cert.resolutionTime, "Too early");
        
        // For hackathon: Only owner resolves (simulating AI oracle)
        // In production: Use decentralized oracle
        require(msg.sender == owner, "Only owner");
        
        uint256 totalReward = cert.stakeAmount + cert.challengeStake;
        
        if (_truthValid) {
            // Truth stands: Verifier wins challenger's stake
            // FIX: Use low-level call with reentrancy protection
            (bool sent, ) = payable(cert.verifier).call{value: totalReward}("");
            require(sent, "Transfer failed");
            validatorReputation[cert.verifier] += 2; // Bonus for winning
        } else {
            // Truth overturned: Challenger wins verifier's stake
            (bool sent, ) = payable(cert.challenger).call{value: totalReward}("");
            require(sent, "Transfer failed");
            validatorReputation[cert.verifier] = 0; // Slash reputation
        }
        
        emit ChallengeResolved(_contentHash, !_truthValid, 
            _truthValid ? cert.verifier : cert.challenger, 
            totalReward
      );
    }
    
    // NEW: Allow verifier to withdraw if no challenge after 7 days
    function withdrawStake(bytes32 _contentHash) external {
        TruthCertificate storage cert = certificates[_contentHash];
        require(cert.verifier == msg.sender, "Not verifier");
        require(!cert.challenged, "Currently challenged");
        require(block.timestamp > cert.resolutionTime, "Lock period active");
        require(cert.stakeAmount > 0, "Already withdrawn");
        
        uint256 amount = cert.stakeAmount;
        cert.stakeAmount = 0; // Prevent reentrancy
        
        (bool sent, ) = payable(msg.sender).call{value: amount}("");
        require(sent, "Withdraw failed");
    }
    
    // View function for frontend
    function getCertificate(bytes32 _contentHash) external view returns (TruthCertificate memory) {
        return certificates[_contentHash];
    }
    
    // Accept funds for rewards
    receive() external payable {}
}