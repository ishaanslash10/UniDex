async function send() {
    let input = document.getElementById("input").value;

    let res = await fetch("https://unidex.onrender.com/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: input })
    });

    let data = await res.json();

    let chat = document.getElementById("chat");
    chat.innerHTML += `<p><b>You:</b> ${input}</p>`;
    chat.innerHTML += `<p><b>UniDex:</b> ${data.response}</p>`;
}