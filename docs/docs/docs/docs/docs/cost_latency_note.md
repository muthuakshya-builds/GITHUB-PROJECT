Cost and Latency Note — Complete Before Final Submission
The tool makes one LLM extraction request per registration entry. For 20 registrations, estimate approximately 20 calls per run (unless batching is explicitly implemented and tested).
Measure
Estimate / evidence
Entries in one run
20 in supplied sample
API calls
20, one per entry
Average latency per call
Measure 5–10 calls and record the observed average
Estimated total processing time
Average latency × number of calls, plus local Python processing
Model and provider
Record the actual Week 12-approved provider/model
Estimated daily cost
Calls per day × measured/quoted cost per call
Do not invent a price. Use the provider's current pricing and actual token usage, or clearly label a rough estimate. Include date and source for any published price.
