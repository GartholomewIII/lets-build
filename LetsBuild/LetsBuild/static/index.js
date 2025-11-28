async function getQuote() {
    const box = document.getElementById("quote-box");

    try {
        // fade out
        box.classList.remove("show");

        // wait for fade-out animation to complete
        await new Promise(resolve => setTimeout(resolve, 300));

        // fetch the quote from Django
        const res = await fetch("/get-quote/");
        const data = await res.json();

        // update text
        document.getElementById("quote-text").textContent = data.text;
        document.getElementById("quote-author").textContent = data.author ? "— " + data.author : "";

        // fade in
        setTimeout(() => {
            box.classList.add("show");
        }, 50);

    } catch (err) {
        console.error("Quote error:", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    getQuote();             // initial load
    setInterval(getQuote, 300000);  // rotate quotes
});
