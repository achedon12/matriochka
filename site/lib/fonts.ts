import { Jersey_10, PT_Serif, Ruslan_Display } from "next/font/google";

// Ruslan Display: a Russian poster face, used large for display only. PT Serif carries the reading.
// Jersey 10, a pixel-grid face, sets game numbers the way Minecraft's interface does (Pixelify Sans was
// tried first: its 5 reads as an S and its 7 as a 1 at data sizes).
export const display = Ruslan_Display({ weight: "400", subsets: ["latin", "latin-ext"], variable: "--f-display", display: "swap" });
export const body = PT_Serif({ weight: ["400", "700"], style: ["normal", "italic"], subsets: ["latin", "latin-ext"], variable: "--f-body", display: "swap" });
export const pixel = Jersey_10({ weight: "400", subsets: ["latin", "latin-ext"], variable: "--f-pixel", display: "swap" });

export const fontVars = `${display.variable} ${body.variable} ${pixel.variable}`;
