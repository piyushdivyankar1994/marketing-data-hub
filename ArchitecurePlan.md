# Campaign Hub Architectural design


## Ingestion Pipleine

### ChunkingStream
The ChunkingStream takes in a character stream and a chunking strategy. 
It will yield the successive chunks based on the strategy.

Chunking strategy is a function that takes characters one at a time and 
returns chunk when it is done and a function to run for getting the
next chunk. 

This strategy is good if we want to deal with large numbers of arbitrary
formats.

### Standard iterative reader implementations
In practice standard data formats like csv, and json are used to transfer
reports. There are csv and ijson libraries that perform the same task 
as chunking strategy but also take care of edge cases and will report
consistent errors. This will be preferred.

### Datamodels
We need to define datamodels that will be used to do the parsing for 
each chunk of the input stream.





