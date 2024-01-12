import { c as create_ssr_component, a as subscribe, b as add_attribute, e as escape } from "../../../chunks/ssr.js";
import { w as writable } from "../../../chunks/index.js";
const css = {
  code: "main.svelte-877in5{display:flex;justify-content:center;align-items:center;height:100vh;background-color:#f0f0f0}.container.svelte-877in5{text-align:center}input.svelte-877in5{display:block;margin:10px auto;padding:8px;font-size:16px;border-radius:5px;border:1px solid #ccc;width:80%}button.svelte-877in5{background-color:#007bff;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;font-size:16px;transition:background-color 0.3s;margin-top:10px;width:80%}button.svelte-877in5:hover{background-color:#0056b3}.create-account-btn.svelte-877in5{background-color:#28a745;margin-top:5px}.create-account-btn.svelte-877in5:hover{background-color:#218838}.error-message.svelte-877in5{color:red;margin-top:10px}",
  map: null
};
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $errorMessage, $$unsubscribe_errorMessage;
  let username = "";
  let password = "";
  const errorMessage = writable("");
  $$unsubscribe_errorMessage = subscribe(errorMessage, (value) => $errorMessage = value);
  $$result.css.add(css);
  $$unsubscribe_errorMessage();
  return ` <main class="svelte-877in5"><div class="container svelte-877in5"><h1 data-svelte-h="svelte-2pvnq6">Sign In</h1> <input type="text" placeholder="Username" class="svelte-877in5"${add_attribute("value", username, 0)}> <input type="password" placeholder="Password" class="svelte-877in5"${add_attribute("value", password, 0)}> <button class="svelte-877in5" data-svelte-h="svelte-1j6heuc">Sign In</button> <button class="create-account-btn svelte-877in5" data-svelte-h="svelte-1kk0px1">Create Account</button> <p class="error-message svelte-877in5">${escape($errorMessage)}</p></div> </main>`;
});
export {
  Page as default
};
