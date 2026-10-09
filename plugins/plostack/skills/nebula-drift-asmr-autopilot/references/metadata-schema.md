# YouTube metadata schema

The publish script accepts a UTF-8 JSON object with these fields:

| Field | Required | Shape | Notes |
|---|---:|---|---|
| `title` | yes | string | Episode title. Keep it clear and non-clickbait. |
| `description` | yes | string | Include the channel/episode context and any asset-credit text supplied by the user. |
| `tags` | no | string array | Use a short, relevant set; do not stuff unrelated keywords. |
| `category_id` | no | string | Defaults to `10` (Music) in the example; confirm if the channel policy changes. |
| `language` | no | string | BCP-47-like language code used for default language fields when supplied. |
| `made_for_kids` | yes | boolean | Explicit audience declaration; never infer it silently. |

The schedule timestamp is passed separately as `--schedule-at` and must include a timezone offset or `Z`. The script keeps the upload private and only sets a future `publishAt` after `--confirm-schedule`.
