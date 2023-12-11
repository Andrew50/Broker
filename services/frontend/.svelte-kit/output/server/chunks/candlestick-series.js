import { s as setContext, g as getContext, c as create_ssr_component, h as createEventDispatcher, i as spread, j as escape_object, k as escape_attribute_value } from "./index2.js";
function context(value) {
  if (typeof value !== "undefined") {
    setContext("lightweight-chart-context", value);
  } else {
    return getContext("lightweight-chart-context");
  }
}
function useSeriesEffect(callback) {
  context();
}
const Chart = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  createEventDispatcher();
  let { container = void 0 } = $$props;
  let { width = 0 } = $$props;
  let { height = 0 } = $$props;
  let { autoSize = void 0 } = $$props;
  let { watermark = void 0 } = $$props;
  let { layout = void 0 } = $$props;
  let { leftPriceScale = void 0 } = $$props;
  let { rightPriceScale = void 0 } = $$props;
  let { overlayPriceScales = void 0 } = $$props;
  let { timeScale = void 0 } = $$props;
  let { crosshair = void 0 } = $$props;
  let { grid = void 0 } = $$props;
  let { localization = void 0 } = $$props;
  let { handleScroll = void 0 } = $$props;
  let { handleScale = void 0 } = $$props;
  let { kineticScroll = void 0 } = $$props;
  let { trackingMode = void 0 } = $$props;
  let { ref = void 0 } = $$props;
  let attrs = {};
  if ($$props.container === void 0 && $$bindings.container && container !== void 0)
    $$bindings.container(container);
  if ($$props.width === void 0 && $$bindings.width && width !== void 0)
    $$bindings.width(width);
  if ($$props.height === void 0 && $$bindings.height && height !== void 0)
    $$bindings.height(height);
  if ($$props.autoSize === void 0 && $$bindings.autoSize && autoSize !== void 0)
    $$bindings.autoSize(autoSize);
  if ($$props.watermark === void 0 && $$bindings.watermark && watermark !== void 0)
    $$bindings.watermark(watermark);
  if ($$props.layout === void 0 && $$bindings.layout && layout !== void 0)
    $$bindings.layout(layout);
  if ($$props.leftPriceScale === void 0 && $$bindings.leftPriceScale && leftPriceScale !== void 0)
    $$bindings.leftPriceScale(leftPriceScale);
  if ($$props.rightPriceScale === void 0 && $$bindings.rightPriceScale && rightPriceScale !== void 0)
    $$bindings.rightPriceScale(rightPriceScale);
  if ($$props.overlayPriceScales === void 0 && $$bindings.overlayPriceScales && overlayPriceScales !== void 0)
    $$bindings.overlayPriceScales(overlayPriceScales);
  if ($$props.timeScale === void 0 && $$bindings.timeScale && timeScale !== void 0)
    $$bindings.timeScale(timeScale);
  if ($$props.crosshair === void 0 && $$bindings.crosshair && crosshair !== void 0)
    $$bindings.crosshair(crosshair);
  if ($$props.grid === void 0 && $$bindings.grid && grid !== void 0)
    $$bindings.grid(grid);
  if ($$props.localization === void 0 && $$bindings.localization && localization !== void 0)
    $$bindings.localization(localization);
  if ($$props.handleScroll === void 0 && $$bindings.handleScroll && handleScroll !== void 0)
    $$bindings.handleScroll(handleScroll);
  if ($$props.handleScale === void 0 && $$bindings.handleScale && handleScale !== void 0)
    $$bindings.handleScale(handleScale);
  if ($$props.kineticScroll === void 0 && $$bindings.kineticScroll && kineticScroll !== void 0)
    $$bindings.kineticScroll(kineticScroll);
  if ($$props.trackingMode === void 0 && $$bindings.trackingMode && trackingMode !== void 0)
    $$bindings.trackingMode(trackingMode);
  if ($$props.ref === void 0 && $$bindings.ref && ref !== void 0)
    $$bindings.ref(ref);
  {
    {
      attrs = Object.assign({}, container);
      delete attrs.ref;
    }
  }
  return `



<div${spread(
    [
      escape_object(attrs),
      {
        style: escape_attribute_value(autoSize ? attrs.style : `width: ${width}px; height: ${height}px;` + attrs.style)
      }
    ],
    {}
  )}>${``}</div>`;
});
const Chart$1 = Chart;
const Candlestick_series = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { lastValueVisible = void 0 } = $$props;
  let { title = void 0 } = $$props;
  let { priceScaleId = void 0 } = $$props;
  let { visible = void 0 } = $$props;
  let { priceLineVisible = void 0 } = $$props;
  let { priceLineSource = void 0 } = $$props;
  let { priceLineWidth = void 0 } = $$props;
  let { priceLineColor = void 0 } = $$props;
  let { priceLineStyle = void 0 } = $$props;
  let { priceFormat = void 0 } = $$props;
  let { baseLineVisible = void 0 } = $$props;
  let { baseLineColor = void 0 } = $$props;
  let { baseLineWidth = void 0 } = $$props;
  let { baseLineStyle = void 0 } = $$props;
  let { autoscaleInfoProvider = void 0 } = $$props;
  let { upColor = void 0 } = $$props;
  let { downColor = void 0 } = $$props;
  let { wickVisible = void 0 } = $$props;
  let { borderVisible = void 0 } = $$props;
  let { borderColor = void 0 } = $$props;
  let { borderUpColor = void 0 } = $$props;
  let { borderDownColor = void 0 } = $$props;
  let { wickColor = void 0 } = $$props;
  let { wickUpColor = void 0 } = $$props;
  let { wickDownColor = void 0 } = $$props;
  let { ref = void 0 } = $$props;
  let { data = [] } = $$props;
  let { reactive = false } = $$props;
  let { markers = [] } = $$props;
  performance.now().toString();
  useSeriesEffect();
  if ($$props.lastValueVisible === void 0 && $$bindings.lastValueVisible && lastValueVisible !== void 0)
    $$bindings.lastValueVisible(lastValueVisible);
  if ($$props.title === void 0 && $$bindings.title && title !== void 0)
    $$bindings.title(title);
  if ($$props.priceScaleId === void 0 && $$bindings.priceScaleId && priceScaleId !== void 0)
    $$bindings.priceScaleId(priceScaleId);
  if ($$props.visible === void 0 && $$bindings.visible && visible !== void 0)
    $$bindings.visible(visible);
  if ($$props.priceLineVisible === void 0 && $$bindings.priceLineVisible && priceLineVisible !== void 0)
    $$bindings.priceLineVisible(priceLineVisible);
  if ($$props.priceLineSource === void 0 && $$bindings.priceLineSource && priceLineSource !== void 0)
    $$bindings.priceLineSource(priceLineSource);
  if ($$props.priceLineWidth === void 0 && $$bindings.priceLineWidth && priceLineWidth !== void 0)
    $$bindings.priceLineWidth(priceLineWidth);
  if ($$props.priceLineColor === void 0 && $$bindings.priceLineColor && priceLineColor !== void 0)
    $$bindings.priceLineColor(priceLineColor);
  if ($$props.priceLineStyle === void 0 && $$bindings.priceLineStyle && priceLineStyle !== void 0)
    $$bindings.priceLineStyle(priceLineStyle);
  if ($$props.priceFormat === void 0 && $$bindings.priceFormat && priceFormat !== void 0)
    $$bindings.priceFormat(priceFormat);
  if ($$props.baseLineVisible === void 0 && $$bindings.baseLineVisible && baseLineVisible !== void 0)
    $$bindings.baseLineVisible(baseLineVisible);
  if ($$props.baseLineColor === void 0 && $$bindings.baseLineColor && baseLineColor !== void 0)
    $$bindings.baseLineColor(baseLineColor);
  if ($$props.baseLineWidth === void 0 && $$bindings.baseLineWidth && baseLineWidth !== void 0)
    $$bindings.baseLineWidth(baseLineWidth);
  if ($$props.baseLineStyle === void 0 && $$bindings.baseLineStyle && baseLineStyle !== void 0)
    $$bindings.baseLineStyle(baseLineStyle);
  if ($$props.autoscaleInfoProvider === void 0 && $$bindings.autoscaleInfoProvider && autoscaleInfoProvider !== void 0)
    $$bindings.autoscaleInfoProvider(autoscaleInfoProvider);
  if ($$props.upColor === void 0 && $$bindings.upColor && upColor !== void 0)
    $$bindings.upColor(upColor);
  if ($$props.downColor === void 0 && $$bindings.downColor && downColor !== void 0)
    $$bindings.downColor(downColor);
  if ($$props.wickVisible === void 0 && $$bindings.wickVisible && wickVisible !== void 0)
    $$bindings.wickVisible(wickVisible);
  if ($$props.borderVisible === void 0 && $$bindings.borderVisible && borderVisible !== void 0)
    $$bindings.borderVisible(borderVisible);
  if ($$props.borderColor === void 0 && $$bindings.borderColor && borderColor !== void 0)
    $$bindings.borderColor(borderColor);
  if ($$props.borderUpColor === void 0 && $$bindings.borderUpColor && borderUpColor !== void 0)
    $$bindings.borderUpColor(borderUpColor);
  if ($$props.borderDownColor === void 0 && $$bindings.borderDownColor && borderDownColor !== void 0)
    $$bindings.borderDownColor(borderDownColor);
  if ($$props.wickColor === void 0 && $$bindings.wickColor && wickColor !== void 0)
    $$bindings.wickColor(wickColor);
  if ($$props.wickUpColor === void 0 && $$bindings.wickUpColor && wickUpColor !== void 0)
    $$bindings.wickUpColor(wickUpColor);
  if ($$props.wickDownColor === void 0 && $$bindings.wickDownColor && wickDownColor !== void 0)
    $$bindings.wickDownColor(wickDownColor);
  if ($$props.ref === void 0 && $$bindings.ref && ref !== void 0)
    $$bindings.ref(ref);
  if ($$props.data === void 0 && $$bindings.data && data !== void 0)
    $$bindings.data(data);
  if ($$props.reactive === void 0 && $$bindings.reactive && reactive !== void 0)
    $$bindings.reactive(reactive);
  if ($$props.markers === void 0 && $$bindings.markers && markers !== void 0)
    $$bindings.markers(markers);
  return `


${``}`;
});
const CandlestickSeries = Candlestick_series;
export {
  Chart$1 as C,
  CandlestickSeries as a
};
