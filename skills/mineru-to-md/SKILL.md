---
name: "mineru-to-md"
description: "Convert supported local documents to Markdown through the local MinerU API in Trae, including PDF, images, DOCX, PPTX, and XLSX, and save the output to a chosen Windows-accessible directory. Use when the user asks to 转 Markdown, 提取 PDF, 解析文档, 图片转 md, 保存为 markdown, or batch-convert supported files. Do not use for web pages, plain text rewriting, or summarization tasks without file conversion."
---

# MinerU To Markdown

Use this skill when the user wants to convert local documents into Markdown files
and save the `.md` output to a chosen directory.

This skill is for agent execution, not end-user documentation.

When the user writes in Chinese, ask required follow-up questions and report saved Markdown paths, skipped files, cleanup warnings, and failures in Simplified Chinese. Keep file paths, API URLs, task IDs, command flags, and JSON keys in their original form.

## Runtime assumptions

- MinerU runs inside WSL + Docker.
- The agent runs on the Windows host.
- Windows can reach MinerU at `http://127.0.0.1:8000`.
- Network mode is `mirror`.

Because of this setup, do **not** use container paths or WSL-internal paths for
API submission. Submit Windows-accessible files directly from the host.

## Invoke when

Invoke this skill when the user asks to:

- convert a PDF to Markdown
- convert an image or scanned document to Markdown
- convert `DOCX`, `PPTX`, or `XLSX` to Markdown
- extract a supported local document into an `.md` file
- save parsed Markdown into a specific directory

Do **not** use this skill for:

- web page to markdown tasks
- plain text rewriting
- general summarization without file conversion
- unsupported file types or remote URLs that are not available as local Windows-accessible files

## Required behavior

Follow these rules exactly:

1. Collect an input source first: 1-2 direct file paths, an input directory, or a UTF-8 list file.
2. Require an output directory.
3. If the user did not specify an output directory, ask before running.
4. For 1-2 simple files, direct file arguments are acceptable, but **must always be wrapped in double quotes** regardless of whether they contain spaces.
5. For more than `2` files, directory conversion, retry batches, or filenames containing smart quotes such as `“”`, use `--input-dir` or `--list-file` so Python collects paths internally. All paths passed to these flags **must also be wrapped in double quotes**.
6. Execute strictly serially.
7. Do not submit multiple parse tasks in parallel.
8. Use the local API at `http://127.0.0.1:8000` unless the user explicitly asks otherwise.
9. Prefer deterministic behavior over convenience.
10. Fail early on invalid paths, unsupported file types, or missing output directory.
11. After successfully saving Markdown on the Windows host, attempt to clean the corresponding container task directory by default.
12. Only keep container-side task artifacts when the user explicitly asks to keep them.
13. Treat per-task cleanup as best effort: report cleanup warnings, but do not treat cleanup failure as conversion failure.
14. Do not create ad hoc batch conversion scripts; use this script's `--input-dir`, `--list-file`, `--dry-run`, `--result-file`, `--failure-list`, and `--skip-existing` options instead.

## Path rules

Accept these path styles:

- normal Windows paths like `D:\docs\a.pdf`
- Windows-accessible `\\wsl$\...` paths
- `/mnt/c/...` style input, which the script can normalize automatically

Do **not** directly execute Linux-only paths like `/home/skyler/a.pdf`.
If the user gives a Linux-only path, ask them for a Windows-accessible path.

## Supported file types

Only use this skill for these extensions:

- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`
- `.jp2`
- `.webp`
- `.gif`
- `.bmp`
- `.doc`
- `.docx`
- `.ppt`
- `.pptx`
- `.xls`
- `.xlsx`

If the file extension is outside this set, stop and tell the user the file type
is not supported by this skill.

## Preflight checklist

Before running the command, confirm all of the following:

1. Exactly one input mode is used: direct files, `--input-dir`, or `--list-file`.
2. Direct file count is `1` or `2`; larger batches use `--input-dir` or `--list-file`.
3. The output directory is known.
4. The task is truly a document-to-Markdown conversion request.
5. The user is not asking for parallel batch conversion.
6. Every input source is Windows-accessible.
7. For uncertain batches, run `--dry-run` first to preview the exact input set instead of writing a temporary enumeration script.
8. For interrupted or repeated batches, use `--skip-existing` unless the user explicitly wants duplicate versioned output or overwrite.

If any item fails, do not execute the script yet.

## Execution flow

Use this decision flow:

1. Identify the input source.
2. Use direct file arguments only for 1-2 simple paths.
3. Use `--input-dir` for a directory of supported documents.
4. Use `--list-file` when filenames contain shell-sensitive characters or when retrying a saved failure list.
5. Validate that every file path is Windows-accessible and supported.
6. Check whether the user provided an output directory.
7. If missing, ask where to save the Markdown files.
8. Run the Python script directly.
9. Read the JSON result from stdout.
10. Treat stderr as progress/error context, not as the authoritative result.
11. Report saved output paths back to the user.
12. Preserve document images by exporting the container parse directory, not by writing only `md_content`.
13. For long batches, add `--result-file` so the final JSON is available even if terminal output scrolls away.
14. For resume workflows, add `--skip-existing` so already exported Markdown files are not submitted again.

## Command to run

Run the Python script directly with an absolute script path:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --output-dir "D:\target\dir" `
  "D:\input\file.pdf"
```

For two files, still run one command only; the script will submit them serially:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --output-dir "D:\target\dir" `
  "D:\input\a.pdf" `
  "D:\input\b.docx"
```

Use `py -3` instead of `python` only when the Windows environment does not expose
`python` on `PATH`.

For a directory batch, do not pass each filename through the shell. Let Python
enumerate the directory:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --input-dir "D:\input\PDF" `
  --output-dir "D:\target\MD"
```

To preview a directory batch without connecting to MinerU:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --input-dir "D:\input\PDF" `
  --dry-run
```

For recursive directory conversion:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --input-dir "D:\input\documents" `
  --recursive `
  --output-dir "D:\target\MD"
```

For paths with smart quotes or other shell-sensitive characters, write a UTF-8
text file with one path per line, then run:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --list-file "D:\input\files.txt" `
  --output-dir "D:\target\MD"
```

For batch work where failures should be easy to retry, add `--failure-list`:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --input-dir "D:\input\PDF" `
  --output-dir "D:\target\MD" `
  --result-file "D:\target\result.json" `
  --failure-list "D:\target\failed.txt"
```

For interrupted batches or safe reruns, add `--skip-existing`:

```powershell
python "C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py" `
  --input-dir "D:\input\PDF" `
  --output-dir "D:\target\MD" `
  --skip-existing `
  --result-file "D:\target\result.json"
```

## Default parameters

The script defaults are:

- `base_url=http://127.0.0.1:8000`
- `backend=hybrid-auto-engine`
- `parse_method=auto`
- `lang=ch`
- `return_md=true`
- `timeout=1800`
- `retry_timeout=3600`
- best-effort container task cleanup after success
- stdout JSON is always the primary result; `--result-file` can write a copy to disk
- existing output is not skipped by default; use `--skip-existing` for resume workflows

Do not override them unless the task clearly requires it.

Large PDFs, scanned documents, and documents with many images may need a longer
first wait. Use `--timeout 3600` when the user mentions large files or prior
timeouts. By default, a task that times out after `1800` seconds is submitted
again once and waited up to `3600` seconds.

## Stability notes

The implementation already performs these checks:

- validates `base_url`
- validates output directory shape
- rejects unsupported file extensions
- rejects missing input files
- supports directory and list-file input without shell-level filename passing
- supports `--dry-run` to preview resolved inputs without contacting MinerU
- reports skipped unsupported files from directory input as `skipped`
- supports `--result-file` for durable JSON output
- can write failed input paths to a UTF-8 failure list for later retry
- supports `--skip-existing` for interrupted batch resume without duplicate `_2` outputs
- rejects suspicious task IDs before container operations
- polls task status serially
- retries transient status/result fetch failures
- retries a timed-out task once with a longer timeout by default
- rejects unknown task states instead of guessing
- writes Markdown via a temporary file before replacing the final `.md`
- attempts to remove `/vllm-workspace/output/<task_id>` after successful host-side save by default
- returns a non-zero exit code only for conversion failures, not cleanup warnings

Rely on these checks, but still do the skill-level preflight before execution.

## Expected script result

On success, stdout is JSON shaped like:

```json
{
  "saved": [
    {
      "input": "D:\\docs\\demo.pdf",
      "output": "D:\\output\\demo\\demo.md",
      "document_dir": "D:\\output\\demo",
      "images_dir": "D:\\output\\demo\\image",
      "container_parse_dir": "/vllm-workspace/output/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/demo",
      "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  ]
}
```

For directory input, stdout may include unsupported files that were skipped:

```json
{
  "saved": [],
  "skipped": [
    {
      "path": "D:\\docs\\notes.txt",
      "reason": "unsupported_extension"
    }
  ]
}
```

When `--skip-existing` is used, stdout may include already completed files:

```json
{
  "saved": [],
  "skipped_existing": [
    {
      "input": "D:\\docs\\demo.pdf",
      "output": "D:\\output\\demo\\demo.md",
      "reason": "output_exists"
    }
  ]
}
```

If some files fail, stdout may also contain:

```json
{
  "saved": [],
  "errors": [
    {
      "input": "D:\\docs\\bad.pdf",
      "error": "..."
    }
  ]
}
```

Treat non-zero exit codes as failure and summarize the error clearly.
Treat stdout JSON as the source of truth.

## Output shape

For stability, the exported host-side result should look like:

- `D:\target\demo\demo.md`
- `D:\target\demo\image\...`

Treat `--output-dir` as the topic directory. Each input document is exported
into its own document directory so the Markdown and images stay self-contained,
which is better for long-term knowledge base management and later wiki use.

Default reruns create versioned output directories like `demo_2` when `demo`
already exists. Use `--skip-existing` for resume workflows, or `--overwrite`
when the user explicitly wants to replace existing document output.

The script rewrites relative image references from `images/...` or
`./images/...` to `image/...` so the Markdown remains directly usable inside
its document directory on the Windows host.

## Failure handling

If the API cannot be reached:

- tell the user MinerU is not reachable from Windows
- ask them to start or restore the WSL-side service
- suggest `mineru api` only when explaining what service needs to be running

If the direct input count is greater than `2`:

- do not run the script
- use `--input-dir` or `--list-file` instead

If the output directory is missing:

- do not run the script
- ask the user where to save the Markdown files

If the path is Linux-only or not Windows-accessible:

- do not run the script
- ask the user for a Windows path or `\\wsl$\...` path

If the extension is unsupported:

- do not run the script
- explain that this skill only handles the supported document/image formats

If filenames contain smart quotes such as `“”`, shell metacharacters, or very
long paths:

- do not pass those paths as direct shell arguments
- use `--input-dir` when all target files are in one directory
- use `--list-file` when the target set is selective

If a batch may need later retry:

- add `--failure-list "D:\target\failed.txt"`
- rerun with `--list-file "D:\target\failed.txt"` after fixing the underlying issue

If a batch was interrupted or might already have completed files:

- add `--skip-existing`
- optionally run `--dry-run --skip-existing --output-dir "D:\target\MD"` first
- use `skipped_existing` to confirm what will not be resubmitted

If the agent needs to inspect the batch before conversion:

- run the same input command with `--dry-run`
- use the JSON `inputs` array as the source of truth
- do not create a temporary Python script just to enumerate files

If the batch is long-running:

- add `--result-file "D:\target\result.json"`
- read that JSON file after completion if stdout is hard to inspect

If stdout is not valid JSON:

- treat the run as failed
- summarize the raw failure signal briefly
- do not guess output paths

If host-side save succeeds but container cleanup fails:

- tell the user the Markdown file was saved successfully
- explicitly report that container artifacts may still remain
- do not claim cleanup succeeded unless the JSON `cleaned` field confirms it
- treat `cleanup_errors` as warnings; the process exit code remains success when all conversions succeeded

## Implementation files

This skill relies on:

- `C:\Users\skyler\.trae\skills\mineru-to-md\scripts\mineru_to_md.py`
