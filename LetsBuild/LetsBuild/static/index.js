async function loadQuotes() {
    try {
        const res = await fetch("/get-quote");
        const data = await res.json();
        window.allQuotes = data.quotes;
        showRandomQuote();
    } catch (err) {
        console.error("Failed to load quotes", err);
    }
}

function showRandomQuote() {
    if (!window.allQuotes || window.allQuotes.length === 0) return;

    const q = window.allQuotes[Math.floor(Math.random() * window.allQuotes.length)];
    document.getElementById("quote").innerText = q.text || "No quote available";
    document.getElementById("author").innerText = q.author || "Unknown";
}

document.addEventListener("DOMContentLoaded", () => {
    loadQuotes();
    setInterval(showRandomQuote, 15000);
});
