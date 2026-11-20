// Writes the amb colour scheme and fonts into the deck's theme after pptxgenjs has saved it,
// and normalises one chart axis attribute that some PowerPoint versions offer to repair.
const fs = require("fs");
const JSZip = require("jszip");

const SLOTS = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"];

async function applyTheme(file, theme) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  for (const name of Object.keys(zip.files)) {
    if (/^ppt\/theme\/theme\d+\.xml$/.test(name)) {
      let xml = await zip.file(name).async("string");
      for (const slot of SLOTS) {
        const re = new RegExp(`<a:${slot}>[\\s\\S]*?</a:${slot}>`);
        xml = xml.replace(re, `<a:${slot}><a:srgbClr val="${theme.colors[slot]}"/></a:${slot}>`);
      }
      xml = xml.replace(/<a:clrScheme name="[^"]*">/, `<a:clrScheme name="${theme.name}">`);
      xml = xml.replace(/(<a:majorFont>\s*<a:latin typeface=")[^"]*"/, `$1${theme.headFontFace}"`);
      xml = xml.replace(/(<a:minorFont>\s*<a:latin typeface=")[^"]*"/, `$1${theme.bodyFontFace}"`);
      zip.file(name, xml);
    }
    if (/^ppt\/charts\/chart\d+\.xml$/.test(name)) {
      const xml = await zip.file(name).async("string");
      zip.file(name, xml.replace(/<c:crossesAt val="autoZero"\/>/g, '<c:crosses val="autoZero"/>'));
    }
  }
  // repack without folder entries, which some cloud editors refuse to open
  const clean = new JSZip();
  for (const [name, entry] of Object.entries(zip.files)) {
    if (!entry.dir) clean.file(name, await entry.async("uint8array"), { createFolders: false });
  }
  fs.writeFileSync(file, await clean.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

module.exports = { applyTheme };
