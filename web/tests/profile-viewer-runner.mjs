import fs from "node:fs";
import { profileViewModel } from "../profile-viewer.mjs";
const result = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
process.stdout.write(JSON.stringify(profileViewModel(result)));
