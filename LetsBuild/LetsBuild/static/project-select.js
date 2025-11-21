document.querySelectorAll(".select").forEach(btn => {
    btn.addEventListener("click", toggleContinue);
});

const continueBtn = document.querySelector(".continue-btn");
let ClickCount = 0;

function toggleContinue() {
    ClickCount++;
    continueBtn.style.display = (ClickCount % 2 === 0) ? "none" : "flex";
}
