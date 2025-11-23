import app from "./index";

const port = process.env.PORT || 8080;

app.listen(port, "0.0.0.0", () => {
  console.log(`[blackroad-os-api] listening on http://0.0.0.0:${port}`);
});
