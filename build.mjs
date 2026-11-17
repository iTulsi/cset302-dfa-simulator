// Publish only browser assets; keep development source and tests out of the site.
import {mkdir, copyFile} from 'node:fs/promises';
await mkdir('dist', {recursive: true});
for (const file of ['index.html', 'dfa.js', 'demo-cases.js']) {
  await copyFile(file, 'dist/' + file);
}
