// Copy buttons for Connect page code blocks. Without JavaScript the blocks stay selectable.
for (const pre of document.querySelectorAll("pre[role=region], pre.agent-prompt")) {
  if (pre.parentElement?.querySelector(":scope > .copy-button")) continue;
  const wrap = document.createElement("div");
  wrap.className = "copy-wrap";
  pre.replaceWith(wrap);
  wrap.append(pre);
  const button = document.createElement("button");
  button.type = "button";
  button.className = "copy-button copy-btn";
  button.textContent = "Copy";
  button.setAttribute("aria-label", `Copy: ${pre.getAttribute("aria-label") || "code block"}`);
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
  wrap.append(button, status);
}
