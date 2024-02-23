# SharedStorage

## Moving components
- Source Laptop
- Destination Laptop
- Server
- Database

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

## Server
- /upload : source wants to upload data to destination.
    - Look at key associated with source machine.
    - Encrypt data using key
    - Make request to destination and add job in destination's queue.
    - Once ready, destination sends destination details to source.
    - source sends info to destination. Main project
    - async process so upload and download can take place. 

- /download: destination wants to download its information from source.
    - Server lets source know about request
    - Source sends information to destination.
    - Source sends message to server when all info is sent.
    - Share destination's key with destination
    - Device downloads the data at location
    - Device decrypts data received at location.
    - Device cross checks data size and lets server know.
    - Server ends job when destination shares data size.    (Potential for hacking)
