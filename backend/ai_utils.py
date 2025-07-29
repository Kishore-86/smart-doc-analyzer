from transformers import pipeline

# Load HuggingFace summarizer model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str, max_length: int = 130, min_length: int = 30, chunk_size: int = 800) -> str:
    """
    Summarize long text by splitting it into chunks to avoid token limits.
    """
    if not text or len(text.strip()) == 0:
        return "No content to summarize."

    try:
        # Split text into chunks (by words)
        words = text.split()
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

        summaries = []
        for chunk in chunks:
            summary = summarizer(
                chunk,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]['summary_text']
            summaries.append(summary)

        # Combine all chunk summaries
        final_summary = " ".join(summaries)
        return final_summary

    except Exception as e:
        # Fallback if model fails
        return f"Summarization unavailable: {str(e)}"
