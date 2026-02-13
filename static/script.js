window.onload = function () {
    const bar = document.querySelector(".progress-bar");
    const score = bar.getAttribute("data-score");
    bar.style.width = score + "%";
};
