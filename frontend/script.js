async function sendMessage() {
    const input = document.getElementById("input");
    const message = input.value;

    const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const data = await res.json();

    const messagesDiv = document.getElementById("messages");
    messagesDiv.innerHTML += `<p><b>Tú:</b> ${message}</p>`;
    messagesDiv.innerHTML += `<p><b>AgroBot:</b> ${data.response}</p>`;

    input.value = "";
}
