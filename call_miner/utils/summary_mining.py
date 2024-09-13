

def condense_summaries(summaries: list[str]):
    # To be implemented
    # Use tiktoken to count the number of tokens in each summary
    # Take as many of the first summaries as long as the number of tokens does not exceed a cutoff
    # Send that to GPT for a short meta-summary
    return ' Later, in another call, the following happened. '.join(summaries[:min(len(summaries), 3)])
