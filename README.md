# P2P DNS and Signature Authority

- Brendan Benshoof

- Andrew Rosen

## What?

We propose a method of distributing Domain Name services across many
or all computers on the internet. To facilitate the authentication of the records
in this new DNS system and to protect against man in the middle attacks we propose
a means of creating a distributed signing authority for SSL certificates.

## Why?
Recent events have yeilded new understanding that the mutually
trusted third party used for most online key exchanges, specifically corperate
signing authorties based in the United States or contries with similar active
survelence programs, have been compromised by the aversery and are being used
to facilitate man in the middle attacks. In order to prevent these attacks we
need a method of authenticating domain name records and signatures those domains
use to secure communications that are difficult to be systematically subverted
by any goverment or corperation.

## How?

- Use a Distributed Hash Table(DHT) to organize a P2P network (Chord)
- Use a varient on NameCoin to secure a list of servers and public keys and to
record DNS registration and transfers.
- Use the DHT to load balence and distribute responsibility for hosting DNS
records and certification keys.

## Distributed Hash Table (Chord)

- Means of organizing communication and responsibility in a p2p network
- Each peer is responsible for a verifiable span of hash values
- Facilitates one-to-one communcation and one-to-many communcation

## Namecoin Variant

- Allows for a shared, immutible and secure public records
- Based on the block chain verification of bitcoin
- One block can include the validation of a new server's public key
- One block can include a DNS record or change
- blocks require a proof of work to authenticate, causing records to be
produced at a semi-fixed rate
- Unlike Bitcoin, 1 block per transaction, thus mining only happens when
a record is required

## Man in the Middle Prevention

- Given: an existing network where nodes have echanged  keys securely
- Given: a new peer who wishes to join the network and share thier public key
    - At least 2 members of the network interogate the new peer for it's public key
    - Those peers that interogated the new peer compare thier results
    - if those results match
        - the new peer mines a block with an authentication record
        - The peers who authenticated the new peer sign that block
        - the new block is distributed across the network
    - if the results do not mach
        - an attack is detected and reported to the new peer by all authenticating servers
        - a member of the network may mine a block with a ban of the compromised peer
        - otherwise the joining process may be repeated in hopes of success

## Distribution of DNS
- Responsibility for serving DNS records is distributed across the network
- Each node of the network acts as a DNS server reverse compatible with the DNS RFC
- Any end user who wishes to use this DNS network sets any node as thier DNS server (and ideally this node is nearby to the client)
- Each node keeps a local hosts file that chaches the results of recent and frequent results
- If a node does not have the DNS record for a request locally or chached. If the request is marked recursive it sends a request for the node across the network. If the request is not marked recursive, a pointer to the closest known peer is given.
- Optionally, if a DNS request is for a domain the P2P DNS is not configured to manage, the request is forwarded to a conventional DNS server
