// Pre-render the app into static HTML.

import fs from 'node:fs'
import path from 'node:path'
import url from 'node:url'

const HEAD_PLACEHOLDER = '<!--app-head-->'
const BODY_PLACEHOLDER = '<!--app-html-->'
const CLIENT_BUILD_PATH = '../dist/client'
const SERVER_BUILD_PATH = '../dist/server'

const __dirname = path.dirname(url.fileURLToPath(import.meta.url))

const _toAbsolute = (p) => path.resolve(__dirname, p)

const manifest = JSON.parse(
  fs.readFileSync(_toAbsolute(CLIENT_BUILD_PATH + '/.vite/ssr-manifest.json'), 'utf-8'),
)
const template = fs.readFileSync(_toAbsolute(CLIENT_BUILD_PATH + '/index.html'), 'utf-8')
const {render} = await import(SERVER_BUILD_PATH + '/entry-server.js')

const _getUrlsToPrerender = () => {
  return fs
    .readdirSync(_toAbsolute('../src/pages'), {recursive: true})
    .filter((file) => file.endsWith('.vue'))
    .map((file) => {
      const name = file.replace(/Page\.vue$/, '').toLowerCase()
      return name === 'home' ? `/` : `/${name}`
    })
}

async function _streamToString(stream) {
  const chunks = [];

  for await (const chunk of stream) {
    chunks.push(Buffer.from(chunk));
  }

  return Buffer.concat(chunks).toString("utf-8");
}

const _populateTemplateWithPreloadLinks = (template, preloadLinks) => {
  const [htmlStart, htmlEnd] = template.split(HEAD_PLACEHOLDER)
  return htmlStart + preloadLinks + htmlEnd
}

const _populateTemplateWithRenderedBody = async (template, bodyContentStream) => {
  const [htmlStart, htmlEnd] = template.split(BODY_PLACEHOLDER)
  return htmlStart + await _streamToString(bodyContentStream) + htmlEnd
}

const _ensureSubdirectoriesExistence = (filePath) => {
  const dirname = path.dirname(filePath);
  if (fs.existsSync(dirname)) {
    return true;
  }
  _ensureSubdirectoriesExistence(dirname);
  fs.mkdirSync(dirname);
}

;(async () => {
  for (const url of _getUrlsToPrerender()) {

    const {stream, preloadLinks} = await render(url, manifest)

    let html = _populateTemplateWithPreloadLinks(template, preloadLinks)
    html = await _populateTemplateWithRenderedBody(html, stream)

    const filePathRelative = `${CLIENT_BUILD_PATH}${url === '/' ? '/index' : url}.html`
    const filePath = _toAbsolute(filePathRelative)

    _ensureSubdirectoriesExistence(filePath)
    fs.writeFileSync(filePath, html)

    console.log('pre-rendered:', filePathRelative)
  }

  // done, delete .vite directory including ssr manifest
  fs.rmSync(_toAbsolute(CLIENT_BUILD_PATH + '/.vite'), { recursive: true })
})()
