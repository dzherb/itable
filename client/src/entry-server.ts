import type { SSRContext } from '@vue/server-renderer'

import { renderToWebStream } from 'vue/server-renderer'
import { createVueApp } from './main'

interface Manifest {
  [key: string]: Array<string>
}

export async function render(url: string, manifest: Manifest) {
  const { app, router } = createVueApp()

  await router.push(url) // todo try catch ?

  // passing SSR context object which will be available via useSSRContext()
  // @vitejs/plugin-vue injects code into a component's setup() that registers
  // itself on ctx.modules. After the render, ctx.modules would contain all the
  // components that have been instantiated during this render call.
  const ctx: SSRContext = {}
  const stream = renderToWebStream(app, ctx)

  const preloadLinks = renderPreloadLinks(ctx.modules, manifest)

  return { stream, preloadLinks }
}

function renderPreloadLinks(modules: Array<string>, manifest: Manifest): string {
  const links: Array<string> = []
  const seen: Set<string> = new Set()
  modules.forEach((id: string) => {
    const files = manifest[id]

    if (!files) return

    files.forEach((file: string) => {
      if (seen.has(file)) return

      seen.add(file)
      if (manifest[file]) {
        for (const depFile of manifest[file]) {
          links.push(renderPreloadLink(depFile))
          seen.add(depFile)
        }
      }
      links.push(renderPreloadLink(file))
    })
  })
  return links.join('')
}

function renderPreloadLink(file: string) {
  const fileParts = file.split('.')
  const extension = fileParts[fileParts.length - 1]

  switch (extension) {
    case 'js':
      return `<link rel="modulepreload" crossorigin href="${file}">`
    case 'css':
      return `<link rel="stylesheet" href="${file}">`
    case 'woff':
      return ` <link rel="preload" href="${file}" as="font" type="font/woff" crossorigin>`
    case 'woff2':
      return ` <link rel="preload" href="${file}" as="font" type="font/woff2" crossorigin>`
    case 'gif':
      return ` <link rel="preload" href="${file}" as="image" type="image/gif">`
    case 'jpg':
    case 'jpeg':
      return ` <link rel="preload" href="${file}" as="image" type="image/jpeg">`
    case 'png':
      return ` <link rel="preload" href="${file}" as="image" type="image/png">`
  }

  return ''
}
