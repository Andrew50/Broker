import { c as create_ssr_component, e as escape, v as validate_component, b as add_attribute } from "../../../chunks/index2.js";
import { w as writable } from "../../../chunks/index.js";
import { ColorType, CrosshairMode } from "lightweight-charts";
import { C as Chart, a as CandlestickSeries } from "../../../chunks/candlestick-series.js";
const _page_svelte_svelte_type_style_lang = "";
const css = {
  code: ".input-overlay.svelte-smk323{position:absolute;top:50%;left:50%;transform:translate(-50%, -50%);background-color:rgba(255, 255, 255, 0.5);padding:20px;border-radius:10px;text-align:center;box-sizing:border-box;z-index:1000;font-size:40pt;text-transform:uppercase}.match-button.svelte-smk323{position:fixed;right:20px;top:20px;background-color:#4CAF50;color:white;border:none;padding:10px 20px;cursor:pointer}.screener-button.svelte-smk323{position:fixed;right:20px;top:120px;background-color:#4CAF50;color:white;border:none;padding:10px 20px;cursor:pointer}.container.svelte-smk323{margin-right:20px}table.svelte-smk323{width:100%;border-collapse:collapse}.popout-menu.svelte-smk323{display:none;position:fixed;right:70px;top:0;background-color:#f9f9f9;min-width:3px;box-shadow:0px 8px 16px 0px rgba(0, 0, 0, 0.2)}.popout-menu.visible.svelte-smk323{display:block}",
  map: null
};
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { match_data_store = writable([]) } = $$props;
  let { match_data = [] } = $$props;
  match_data_store.subscribe((value) => {
    try {
      match_data = JSON.parse(value);
    } catch {
      match_data = value;
    }
  });
  let screener_data_store = writable();
  screener_data_store.subscribe((value) => {
  });
  let { chart_data_store = writable([
    {
      time: "2018-10-19",
      open: 180.34,
      high: 180.99,
      low: 178.57,
      close: 179.85
    }
  ]) } = $$props;
  let { chart_data } = $$props;
  chart_data_store.subscribe((value) => {
    console.log(value);
    try {
      chart_data = JSON.parse(value);
    } catch {
      chart_data = value;
    }
  });
  let innerWidth;
  let innerHeight;
  let TickerBox;
  let TickerBoxValue = "";
  let chartTicker;
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
  if ($$props.match_data_store === void 0 && $$bindings.match_data_store && match_data_store !== void 0)
    $$bindings.match_data_store(match_data_store);
  if ($$props.match_data === void 0 && $$bindings.match_data && match_data !== void 0)
    $$bindings.match_data(match_data);
  if ($$props.chart_data_store === void 0 && $$bindings.chart_data_store && chart_data_store !== void 0)
    $$bindings.chart_data_store(chart_data_store);
  if ($$props.chart_data === void 0 && $$bindings.chart_data && chart_data !== void 0)
    $$bindings.chart_data(chart_data);
  $$result.css.add(css);
  return `



<div class="container svelte-smk323"><div class="button-container"><button class="match-button svelte-smk323"><div>M</div>
        <div>A</div>
        <div>T</div>
        <div>C</div>
        <div>H</div></button>
    <button class="screener-button svelte-smk323"><div>S</div>
        <div>C</div>
        <div>R</div>
        <div>E</div>
        <div>E</div>
        <div>N</div>
        <div>E</div>
        <div>R</div></button>

    <div class="${["popout-menu svelte-smk323", ""].join(" ").trim()}" style="${"min-height: " + escape(innerHeight, true) + "px;"}">${``}</div>
    <div class="${["popout-menu svelte-smk323", ""].join(" ").trim()}" style="${"min-height: " + escape(innerHeight, true) + "px;"}">${``}</div></div></div>
${validate_component(Chart, "Chart").$$render($$result, Object.assign({}, { width: innerWidth - 300 }, { height: innerHeight - 40 }, options), {}, {
    default: () => {
      return `${validate_component(CandlestickSeries, "CandlestickSeries").$$render(
        $$result,
        {
          data: chart_data,
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
      )}`;
    }
  })}
${escape(chartTicker)}
<a href="/test">test</a>

<input class="input-overlay svelte-smk323" style="${"display: " + escape(TickerBoxVisible, true) + ";"}"${add_attribute("this", TickerBox, 0)}${add_attribute("value", TickerBoxValue, 0)}>`;
});
export {
  Page as default
};
