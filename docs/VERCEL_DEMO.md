# Public Vercel demonstration

The root `index.py` entrypoint forces `SEHAT_ENV=demo`. In this mode the app uses empty stores under the temporary directory, rejects all write requests except loading the two synthetic prescription examples, and sends `Cache-Control: no-store` on responses. `.vercelignore` and `vercel.json` exclude the repository `data/` directory, local environment files, and test/development folders from the deployment bundle.

The Vercel deployment is a public, read-only product demonstration. It must not accept patient or personal health information. It does not provide durable records, user accounts, or nationwide health coverage. The normal production startup lock remains in place; the `demo` mode is not production mode.

Deploy after signing in to Vercel:

```bash
npx vercel deploy --prod
```

For current Vercel Python/ASGI behavior, see the [Python runtime documentation](https://vercel.com/docs/functions/runtimes/python) and [Starlette starter](https://vercel.com/templates/backend/starlette-starter).
