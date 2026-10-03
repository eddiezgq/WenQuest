# 第三方代码

| 文件 | 来源 | 许可证 | 重建 |
|---|---|---|---|
| `y2d.min.js` | yosys2digitaljs 0.10.3（`yosys2digitaljs/core`）及其依赖，经 esbuild 打包 | BSD-2-Clause（依赖：3vl、big-integer、hashmap、topsort、assert，均为宽松许可） | `npm i yosys2digitaljs@0.10.3 && npx esbuild@0.25.11 y2d-entry.js --bundle --minify --format=iife --platform=browser --outfile=y2d.min.js` |

运行时从 CDN（或问渠服务器）加载、不进仓库的：eecircuit-engine 1.8.0（ngspice，MIT/BSD）、@yowasp/yosys 0.70.62-dev.1236（ISC）、digitaljs 0.14.2（BSD-2-Clause）。
