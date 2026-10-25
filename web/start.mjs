// Adds a copy button to each prompt on the start page. Without JavaScript the prompts stay selectable text.
for (const pre of document.querySelectorAll("pre.agent-prompt")) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "copy-button";
  button.textContent = "Copy";
  button.setAttribute("aria-label", `Copy: ${pre.getAttribute("aria-label")}`);
  const status = document.createElement("span");
  status.className = "visually-hidden";
  status.setAttribute("aria-live", "polite");
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(pre.textContent);
      button.textContent = "Copied";
      status.textContent = "Copied to the clipboard.";
    } catch {
      const range = document.createRange();
      range.selectNodeContents(pre);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = "Selected";
      status.textContent = "Text selected. Copy it with your device's copy command.";
    }
    setTimeout(() => { button.textContent = "Copy"; }, 2400);
  });
  pre.after(button, status);
}
