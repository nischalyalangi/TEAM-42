function askTutor() {
    const tier = document.getElementById("tier").value;
    const question = document.getElementById("question").value;
    const responseBox = document.getElementById("response");

    if (question.trim() === "") {
        responseBox.innerText = "Please enter a question.";
        return;
    }

    // Simulated backend logic
    let response = "";

    if (tier === "foundational") {
        response = "Classification assigns data into categories. It is evaluated using accuracy, precision, recall, and F1-score.";
    } else if (tier === "competent") {
        response = "Classification models are evaluated using accuracy, precision, recall, and F1-score. Precision and recall help understand model performance on imbalanced data.";
    } else {
        response = "Advanced evaluation focuses on precision-recall tradeoffs, ROC curves, and the impact of class imbalance on model performance.";
    }

    responseBox.innerText = response;
}
