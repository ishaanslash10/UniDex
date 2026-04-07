async function send() {
    let input = document.getElementById("input").value;

    let res = await fetch(
        `https://unidex.onrender.com/ask?query=${input}&reg_no=23bcon0479&section=5A`,
        {
            method: "POST"
        }
    );
    let data = await res.json();

    let chat = document.getElementById("chat");
    chat.innerHTML += `<p><b>You:</b> ${input}</p>`;
    chat.innerHTML += `<p><b>UniDex:</b> ${data.response || data.answer || data.message || "No response"}</p>`;
}