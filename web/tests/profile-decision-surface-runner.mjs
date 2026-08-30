import { renderProfileResult, SYNTHETIC_CISO_PROFILE_RESULT } from "../profile-viewer.mjs";
const attributes = {};
const target = { innerHTML: "", setAttribute: (name, value) => attributes[name] = value, focus: () => attributes.focused = true };
const view = renderProfileResult(SYNTHETIC_CISO_PROFILE_RESULT, { getElementById: id => id === "profile-result" ? target : null });
process.stdout.write(JSON.stringify({ attributes, html: target.innerHTML, view }));
