import { c as create_ssr_component, e as escape } from "../../../chunks/ssr.js";
import { w as writable } from "../../../chunks/index.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let data1 = writable();
  let data1val;
  data1.subscribe((value) => {
    data1val = value;
  });
  return `<div><form data-svelte-h="svelte-1hoe0xu"><div><input type="text" name="func" placeholder="func" required></div> <div><input type="text" name="arg1" placeholder="arg1"></div> <div><input type="text" name="arg2" placeholder="arg2"></div> <div><input type="text" name="arg3" placeholder="arg3"></div> <div><input type="text" name="arg4" placeholder="arg4"></div> <div><input type="text" name="arg5" placeholder="arg5"></div> <div><input type="text" name="arg6" placeholder="arg6"></div> <input type="submit" value="FETCH"></form> <p>Result: ${escape(data1val)}</p></div>`;
});
export {
  Page as default
};
