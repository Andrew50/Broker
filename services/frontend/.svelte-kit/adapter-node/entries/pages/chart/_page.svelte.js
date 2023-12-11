import { d as get_store_value, c as create_ssr_component, a as subscribe, e as escape, b as add_attribute, f as each, v as validate_component } from "../../../chunks/index2.js";
import { w as writable } from "../../../chunks/index.js";
import { ColorType, CrosshairMode } from "lightweight-charts";
import { C as Chart, a as CandlestickSeries } from "../../../chunks/candlestick-series.js";
import { B as BROWSER } from "../../../chunks/prod-ssr.js";
const browser = BROWSER;
function client_method(key) {
  {
    if (key === "before_navigate" || key === "after_navigate" || key === "on_navigate") {
      return () => {
      };
    } else {
      const name_lookup = {
        disable_scroll_handling: "disableScrollHandling",
        preload_data: "preloadData",
        preload_code: "preloadCode",
        invalidate_all: "invalidateAll"
      };
      return () => {
        throw new Error(`Cannot call ${name_lookup[key] ?? key}(...) on the server`);
      };
    }
  }
}
const goto = /* @__PURE__ */ client_method("goto");
let screener_data = writable([]);
let chart_data = writable([]);
let match_data = writable([[], [], []]);
let auth_data = writable(null);
let setups_list = writable([]);
let watchlist_data = writable({});
function getAuthHeaders() {
  const token = get_store_value(auth_data);
  return token ? { "Authorization": `Bearer ${token}` } : {};
}
async function data_request(bind_variable, func, ...args) {
  const url = `http://localhost:5057/data`;
  const payload = {
    function: func,
    arguments: args
  };
  console.log("Request sent to:", url, "func:", func, "args:", args);
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders()
      },
      body: JSON.stringify(payload)
      // Send the payload as a stringified JSON in the body
    });
    if (!response.ok) {
      throw new Error("POST response not ok");
    }
    let result = await response.json();
    try {
      result = JSON.parse(result);
    } catch (error) {
    }
    if (bind_variable == null) {
      return result;
    } else {
      bind_variable.set(result);
    }
  } catch (error) {
    console.error("Error during backend request:", error);
    bind_variable.set(null);
  }
}
const Match_svelte_svelte_type_style_lang = "";
const css$9 = {
  code: "@import './style.css';",
  map: null
};
const Match = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $match_data, $$unsubscribe_match_data;
  $$unsubscribe_match_data = subscribe(match_data, (value) => $match_data = value);
  let ticker = "JBL";
  let tf = "1d";
  let dt = "2023-10-03";
  let { visible = false } = $$props;
  let innerHeight;
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  $$result.css.add(css$9);
  $$unsubscribe_match_data();
  return `<div class="${["popout-menu", visible ? "visible" : ""].join(" ").trim()}" style="${"min-height: " + escape(innerHeight, true) + "px;"}">${visible ? `<form><div class="form-group"><input type="text" id="ticker" name="ticker" placeholder="Enter Ticker" required${add_attribute("value", ticker, 0)}></div>
            <div class="form-group"><input type="text" id="tf" name="tf" placeholder="Enter TF" required${add_attribute("value", tf, 0)}></div>
            <div class="form-group"><input type="text" id="dt" name="dt" placeholder="Enter Date Time"${add_attribute("value", dt, 0)}></div>
            <div class="form-group"><input type="submit" value="FETCH"></div></form>
        ${$match_data.length > 0 ? `<table><thead><tr><th>Ticker Symbol</th>
                        <th>Timestamp</th>
                        <th>Value</th></tr></thead>
                <tbody>${each($match_data, (item) => {
    return `<tr>
                            <td>${escape(item[0])}</td> 
                            <td>${escape(item[1])}</td> 
                            <td>${escape(item[2])}</td> 
                        </tr>`;
  })}</tbody></table>` : ``}` : ``}
</div>`;
});
const Table_svelte_svelte_type_style_lang = "";
const css$8 = {
  code: ".scrollable-table.svelte-8p5mmp.svelte-8p5mmp{overflow-y:auto;max-height:400px}.context-menu.svelte-8p5mmp.svelte-8p5mmp{position:absolute;background-color:white;border:1px solid #ccc;padding:10px;z-index:10;display:flex;flex-direction:column}.context-menu.svelte-8p5mmp button.svelte-8p5mmp{margin-top:5px}",
  map: null
};
const Table = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { headers = [] } = $$props;
  let { rows = [] } = $$props;
  let { onRowClick } = $$props;
  let { clickHandlerArgs = [] } = $$props;
  if ($$props.headers === void 0 && $$bindings.headers && headers !== void 0)
    $$bindings.headers(headers);
  if ($$props.rows === void 0 && $$bindings.rows && rows !== void 0)
    $$bindings.rows(rows);
  if ($$props.onRowClick === void 0 && $$bindings.onRowClick && onRowClick !== void 0)
    $$bindings.onRowClick(onRowClick);
  if ($$props.clickHandlerArgs === void 0 && $$bindings.clickHandlerArgs && clickHandlerArgs !== void 0)
    $$bindings.clickHandlerArgs(clickHandlerArgs);
  $$result.css.add(css$8);
  Object.keys(get_store_value(watchlist_data));
  return `${``}


${rows.length > 0 ? `<div class="scrollable-table svelte-8p5mmp"><table><thead><tr>${each(headers, (header) => {
    return `<th>${escape(header)}</th>`;
  })}</tr></thead>
        <tbody>${each(rows, (item) => {
    return `<tr>${each(item, (cell) => {
      return `<td>${escape(cell)}</td>`;
    })}
                </tr>`;
  })}</tbody></table></div>` : ``}`;
});
const Screener_svelte_svelte_type_style_lang = "";
const css$7 = {
  code: "@import './style.css';.input-form.svelte-wtc9ax{display:flex;flex-direction:column;gap:10px}.form-group.svelte-wtc9ax{display:flex;flex-direction:column}",
  map: null
};
const Screener = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $setups_list, $$unsubscribe_setups_list;
  let $screener_data, $$unsubscribe_screener_data;
  $$unsubscribe_setups_list = subscribe(setups_list, (value) => $setups_list = value);
  $$unsubscribe_screener_data = subscribe(screener_data, (value) => $screener_data = value);
  let ticker = "";
  let datetime = "";
  let selectedSetups = new Set($setups_list.map((subArray) => subArray[0]));
  console.log("god", selectedSetups);
  let { visible = false } = $$props;
  let innerHeight;
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  $$result.css.add(css$7);
  $$unsubscribe_setups_list();
  $$unsubscribe_screener_data();
  return `<div class="${["popout-menu svelte-wtc9ax", visible ? "visible" : ""].join(" ").trim()}" style="${"min-height: " + escape(innerHeight, true) + "px;"}">${visible ? `
        ${each($setups_list, (setup) => {
    return `<div><label class="setup-item svelte-wtc9ax"><input type="checkbox" checked>
                ${escape(setup[0])}
                </label>
            </div>`;
  })}

        <form class="input-form svelte-wtc9ax"><div class="form-group svelte-wtc9ax"><label for="ticker">Ticker:</label>
                <input type="text" id="ticker" placeholder="Ticker"${add_attribute("value", ticker, 0)}></div>
            <div class="form-group svelte-wtc9ax"><label for="datetime">Datetime:</label>
                <input type="text" id="datetime" placeholder="YYYY-MM-DD HH:MM"${add_attribute("value", datetime, 0)}></div>
            <input type="submit" value="Screen"></form>
        
        ${validate_component(Table, "Table").$$render(
    $$result,
    {
      headers: ["Ticker", "Value"],
      rows: $screener_data,
      onRowClick: data_request,
      clickHandlerArgs: [chart_data, "chart", "Ticker", "1d"]
    },
    {},
    {}
  )}
        
       
        ` : ``}
</div>`;
});
const Chart_svelte_svelte_type_style_lang = "";
const css$6 = {
  code: ".input-overlay.svelte-pycug5{position:absolute;top:50%;left:50%;transform:translate(-50%, -50%);background-color:rgba(255, 255, 255, 0.5);padding:20px;border-radius:10px;text-align:center;box-sizing:border-box;z-index:2000;font-size:40pt;text-transform:uppercase}",
  map: null
};
const Chart_1 = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $chart_data, $$unsubscribe_chart_data;
  $$unsubscribe_chart_data = subscribe(chart_data, (value) => $chart_data = value);
  let innerWidth;
  let innerHeight;
  let TickerBox;
  let TickerBoxValue = "";
  let TickerBoxVisible = "none";
  const options = {
    layout: {
      background: { type: ColorType.Solid, color: "#000000" },
      textColor: "rgba(255, 255, 255, 0.9)"
    },
    grid: {
      vertLines: { color: "rgba(197, 203, 206, 0.5)" },
      horzLines: { color: "rgba(197, 203, 206, 0.5)" }
    },
    crosshair: { mode: CrosshairMode.Magnet },
    rightPriceScale: { borderColor: "rgba(197, 203, 206, 0.8)" },
    timeScale: { borderColor: "rgba(197, 203, 206, 0.8)" }
  };
  $$result.css.add(css$6);
  $$unsubscribe_chart_data();
  return `



${validate_component(Chart, "Chart").$$render($$result, Object.assign({}, { width: innerWidth - 500 }, { height: innerHeight - 20 }, options), {}, {
    default: () => {
      return `${$chart_data && Array.isArray($chart_data) && $chart_data.length > 0 ? `${validate_component(CandlestickSeries, "CandlestickSeries").$$render(
        $$result,
        {
          data: $chart_data,
          reactive: true,
          upColor: "rgba(0,255, 0, 1)",
          downColor: "rgba(255, 0, 0, 1)",
          borderDownColor: "rgba(255, 0, 0, 1)",
          borderUpColor: "rgba(0,255, 0, 1)",
          wickDownColor: "rgba(255, 0, 0, 1)",
          wickUpColor: "rgba(0,255, 0, 1)"
        },
        {},
        {}
      )}` : ``}`;
    }
  })}

<input class="input-overlay svelte-pycug5" style="${"display: " + escape(TickerBoxVisible, true) + ";"}"${add_attribute("this", TickerBox, 0)}${add_attribute("value", TickerBoxValue, 0)}>`;
});
const Trainer_svelte_svelte_type_style_lang = "";
const css$5 = {
  code: "@import './style.css';.inp.svelte-15wzxpo{width:100px}.error-message.svelte-15wzxpo{color:red}.setup-details.svelte-15wzxpo{margin-top:20px}",
  map: null
};
const Trainer = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $$unsubscribe_current_instance;
  let $setups_list, $$unsubscribe_setups_list;
  $$unsubscribe_setups_list = subscribe(setups_list, (value) => $setups_list = value);
  let { visible = false } = $$props;
  let setupName = "";
  let setupTimeframe = "";
  let setupLength = 0;
  let helper_store = writable({});
  let selected_setup = "";
  let instance_queue = {};
  let current_instance = writable([]);
  $$unsubscribe_current_instance = subscribe(current_instance, (value) => value);
  try {
    setups_list.forEach((setup) => {
      instance_queue[setup[0]] = [];
    });
  } catch {
  }
  helper_store.subscribe((value) => {
    Object.keys(value).forEach((st) => {
      const newScore = value[st].score;
      setups_list.update((list) => {
        return list.map((setup) => {
          if (setup[0] === st) {
            setup[4] = newScore;
          }
          return setup;
        });
      });
    });
  });
  current_instance.subscribe((value) => {
    data_request(chart_data, "chart", ...value);
  });
  function select_setup(setup) {
    selected_setup = setup;
    data_request(current_instance, "get instance", selected_setup);
  }
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  $$result.css.add(css$5);
  $$unsubscribe_current_instance();
  $$unsubscribe_setups_list();
  return `<div class="${["popout-menu", visible ? "visible" : ""].join(" ").trim()}">${visible ? `<div>${validate_component(Table, "Table").$$render(
    $$result,
    {
      headers: ["Name", "TF", "Length", "Samples", "Score"],
      rows: $setups_list,
      onRowClick: select_setup,
      clickHandlerArgs: ["Name"]
    },
    {},
    {}
  )}</div>

        ${``}

        ${selected_setup == "" ? `<div class="setup-details svelte-15wzxpo">
               
                <div class="controls"><input class="inp svelte-15wzxpo" type="text" placeholder="Setup Name"${add_attribute("value", setupName, 0)}>
            
                    <input class="inp svelte-15wzxpo" type="text" placeholder="Setup Timeframe"${add_attribute("value", setupTimeframe, 0)}>
                    <input class="inp svelte-15wzxpo" type="text" placeholder="Setup Length"${add_attribute("value", setupLength, 0)}></div>
                    <div><button>Create Setup</button>
                    <button>Delete Setup</button></div></div>` : ``}
        
        ${selected_setup ? `<button>Train</button>
         <p>Is this a ${escape(selected_setup)}? </p>
         <div><button>Yes  </button>
                <button>No </button>
                <button>Back </button></div>` : ``}` : ``}
</div>`;
});
const Study_svelte_svelte_type_style_lang = "";
const css$4 = {
  code: "@import './style.css';.large-textarea.svelte-1wpv272{width:100%;height:200px;padding:10px;font-size:1em;box-sizing:border-box;resize:vertical}",
  map: null
};
const Study = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $setups_list, $$unsubscribe_setups_list;
  $$unsubscribe_setups_list = subscribe(setups_list, (value) => $setups_list = value);
  let { visible = false } = $$props;
  let innerHeight;
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  $$result.css.add(css$4);
  $$unsubscribe_setups_list();
  return `<div class="${["popout-menu", visible ? "visible" : ""].join(" ").trim()}" style="${"min-height: " + escape(innerHeight, true) + "px;"}">${visible ? `<div><div><select><option disabled selected value="">Select a watchlist</option>${each($setups_list, (key) => {
    return `<option${add_attribute("value", key[0], 0)}>${escape(key[0])}</option>`;
  })}</select>
        <button>Fetch [dev]</button></div>

        <div><textarea class="large-textarea svelte-1wpv272" placeholder="Enter text here">${escape("")}</textarea></div>
        <div><button>Next</button></div></div>` : ``}
</div>`;
});
const Account_svelte_svelte_type_style_lang = "";
const css$3 = {
  code: "@import './style.css';",
  map: null
};
const Account = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { visible = false } = $$props;
  let innerHeight;
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  $$result.css.add(css$3);
  return `<div class="${["popout-menu", visible ? "visible" : ""].join(" ").trim()}" style="${"min-height: " + escape(innerHeight, true) + "px;"}">${visible ? `<p>account</p><p></p>` : ``}
</div>`;
});
const Settings_svelte_svelte_type_style_lang = "";
const css$2 = {
  code: "@import './style.css';",
  map: null
};
const Settings = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { visible = false } = $$props;
  let innerHeight;
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  $$result.css.add(css$2);
  return `<div class="${["popout-menu", visible ? "visible" : ""].join(" ").trim()}" style="${"min-height: " + escape(innerHeight, true) + "px;"}">${visible ? `<p>settings</p><p></p>` : ``}
</div>`;
});
const Watchlist_svelte_svelte_type_style_lang = "";
const css$1 = {
  code: "@import './style.css';",
  map: null
};
const Watchlist = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let watchlist_keys;
  let $watchlist_data, $$unsubscribe_watchlist_data;
  $$unsubscribe_watchlist_data = subscribe(watchlist_data, (value) => $watchlist_data = value);
  let { visible = false } = $$props;
  let watchlist_name = "";
  let ticker_name = "";
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  $$result.css.add(css$1);
  watchlist_keys = Object.keys($watchlist_data);
  $$unsubscribe_watchlist_data();
  return `<div class="${["popout-menu", visible ? "visible" : ""].join(" ").trim()}">${visible ? `<div><select><option disabled selected value="">Select a watchlist</option>${each(watchlist_keys, (key) => {
    return `<option${add_attribute("value", key, 0)}>${escape(key)}</option>`;
  })}</select>
        <input type="text" placeholder="Name"${add_attribute("value", watchlist_name, 0)}>
        <button>Create New </button></div>
        <div><input type="text" placeholder="Ticker"${add_attribute("value", ticker_name, 0)}>
            <button>Add Ticker </button></div>
        ${``}` : ``}
</div>`;
});
const _page_svelte_svelte_type_style_lang = "";
const css = {
  code: ".button-container.svelte-1247y1f{position:fixed;right:20px;top:20px}.button.svelte-1247y1f{background-color:#007bff;color:white;border:none;padding:10px 10px;margin-bottom:7px;cursor:pointer;border-radius:5px;font-size:10px;transition:background-color 0.3s;display:flex;flex-direction:column;align-items:center;justify-content:center}.button.svelte-1247y1f:hover{background-color:#0056b3}.icon.svelte-1247y1f{width:30px;height:30px}",
  map: null
};
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let isAuthenticated;
  let $auth_data, $$unsubscribe_auth_data;
  $$unsubscribe_auth_data = subscribe(auth_data, (value) => $auth_data = value);
  let active_menu = "";
  $$result.css.add(css);
  isAuthenticated = $auth_data !== null;
  {
    if (!isAuthenticated && browser) {
      goto("/auth");
    }
  }
  $$unsubscribe_auth_data();
  return `<div class="button-container svelte-1247y1f"><button class="button svelte-1247y1f"><im class="icon svelte-1247y1f" src="/watchlist.png" alt=""></im></button>
    <button class="button svelte-1247y1f"><img class="icon svelte-1247y1f" src="/match.png" alt=""></button>
    <button class="button svelte-1247y1f"><img class="icon svelte-1247y1f" src="/screener.png" alt=""></button>
    <button class="button svelte-1247y1f"><img class="icon svelte-1247y1f" src="/trainer.png" alt=""></button>
    <button class="button svelte-1247y1f"><img class="icon svelte-1247y1f" src="/study.png" alt=""></button>
    <button class="button svelte-1247y1f"><img class="icon svelte-1247y1f" src="/account.png" alt=""></button>
    <button class="button svelte-1247y1f"><im class="icon svelte-1247y1f" src="/settings.png" alt=""></im></button></div>

${validate_component(Watchlist, "Watchlist").$$render($$result, { visible: active_menu == "watchlist" }, {}, {})}
${validate_component(Match, "Match").$$render($$result, { visible: active_menu == "match" }, {}, {})}
${validate_component(Screener, "Screener").$$render($$result, { visible: active_menu == "screener" }, {}, {})}
${validate_component(Trainer, "Trainer").$$render($$result, { visible: active_menu == "trainer" }, {}, {})}
${validate_component(Study, "Study").$$render($$result, { visible: active_menu == "study" }, {}, {})}
${validate_component(Account, "Account").$$render($$result, { visible: active_menu == "account" }, {}, {})}
${validate_component(Settings, "Settings").$$render($$result, { visible: active_menu == "settings" }, {}, {})}
${validate_component(Chart_1, "Chart").$$render($$result, {}, {}, {})}`;
});
export {
  Page as default
};
