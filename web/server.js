const { createServer } = require("https");
const { parse } = require("url");
const next = require("next");
const fs = require("fs");

const dev = process.env.NODE_ENV !== "production";
const app = next({ dev });
const handle = app.getRequestHandler();

const httpsOptions = {
  key: fs.readFileSync("/Users/jonathancalixte/localhost.key"),
  cert: fs.readFileSync("/Users/jonathancalixte/localhost.crt"),
};

app.prepare().then(() => {
  createServer(httpsOptions, (req, res) => {
    const parsedUrl = parse(req.url, true);
    handle(req, res, parsedUrl);
  }).listen(3000, "0.0.0.0", (err) => {
    if (err) throw err;
    console.log("> Ready on https://0.0.0.0:3000");
    console.log("> You can access the app using your local IP address");
  });
});
