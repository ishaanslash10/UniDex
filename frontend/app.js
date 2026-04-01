const reg = "23BCON0479";
const section = "A";

function addMessage(text, type) {
    const chat = document.getElementById("chat");

    const div = document.createElement("div");
    div.classList.add("message", type);
    div.innerText = text;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function askAI() {
    let q = document.getElementById("question").value;

    if (!q.trim()) return;

    addMessage(q, "user");

    const loading = document.createElement("div");
    loading.classList.add("message", "bot");
    loading.innerText = "Thinking...";
    document.getElementById("chat").appendChild(loading);

    try {
        let res = await fetch(
            `http://127.0.0.1:8000/ask?query=${encodeURIComponent(q)}&reg_no=${reg}&section=${section}`
        );

        let data = await res.json();

        loading.innerText =
            data.response || data.answer || JSON.stringify(data.data);

    } catch (err) {
        loading.innerText = "Something went wrong";
    }
}