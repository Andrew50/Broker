import { chart } from './class.js';
import { math } from './math.js';

chart.prototype.getDataBounds = function (dataSliced) {
    //const dates = this.data.map(dataPoint => new Date(dataPoint[0]));
    const high = dataSliced.map(dataPoint => dataPoint[2]);
    const low = dataSliced.map(dataPoint => dataPoint[3]);
    // Find the minimum and maximum dates
    //const minX = new Date(Math.min(...dates.map(date => date.getTime())));
    //const maxX = new Date(Math.max(...dates.map(date => date.getTime())));
    const minX = 0;
    const maxX = dataSliced.length;
    const maxY = Math.max(...high);
    const minY = Math.min(...low);
    const bounds = {
        left: minX,
        right: maxX,
        top: maxY,
        bottom: minY
    }
    return bounds;
}

chart.prototype.draw = function (cursor) {
    const { ctx, canvas } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.pixelBounds = this.getPixelBounds();
    if (this.queryValid) {
        const rightVisibleIndex = this.data.length + Math.ceil(this.a);
        const screenSizeInCandles = Math.floor((this.pixelBounds.right) / this.candleWidth)
        //console.log(screenSizeInCandles, this.pixelBounds.right, this.candleWidth)
        const dataSliced = this.data.slice(rightVisibleIndex - screenSizeInCandles,rightVisibleIndex);
        this.dataBounds = this.getDataBounds(dataSliced);
        let i = 0;
        for (const candleStick of dataSliced) {
            this.drawData(i, candleStick);
            i++;
        }
        if (dataSliced.length > 0) {
            this.drawAxes(dataSliced);
        }
        if (cursor) {
            this.drawCursor();
        }
    }
    
}

chart.prototype.getPixelBounds = function () {
    const { canvas, margin } = this;
    const bounds = {
        right: canvas.width - margin + this.candleWidth,
        left: 0,
        top:0,
        topC: canvas.height * .05,
        bottomC: canvas.height * .7,
        bottom: canvas.height - margin,
    }
    return bounds;
}

chart.prototype.drawData = function (i, candleStick) {
    const { ctx, data, dataBounds, pixelBounds } = this;
    const pixelLoc = [
        math.remap(dataBounds.left, dataBounds.right, pixelBounds.left, pixelBounds.right, i),
        math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.topC, pixelBounds.bottomC, candleStick[1]),
        math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.topC, pixelBounds.bottomC, candleStick[2]),
        math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.topC, pixelBounds.bottomC, candleStick[3]),
        math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.topC, pixelBounds.bottomC, candleStick[4])
    ];
    if (pixelLoc[1] < pixelLoc[4]) {
        ctx.fillStyle = 'red';
    }
    else {
        ctx.fillStyle = 'green';
    }
    const xOffset = Math.abs(this.a - Math.floor(this.a)) * this.candleWidth;
    //const xOffset = 0;
    ctx.fillRect(pixelLoc[0] - xOffset, ((pixelLoc[1] + pixelLoc[4]) - Math.abs(pixelLoc[1] - pixelLoc[4])) / 2, this.candleWidth, Math.abs(pixelLoc[1] - pixelLoc[4]));
    ctx.fillRect(pixelLoc[0] - xOffset + this.candleWidth / 2 - this.wickWidth/2, ((pixelLoc[2] + pixelLoc[3]) - Math.abs(pixelLoc[2] - pixelLoc[3])) / 2, this.wickWidth, Math.abs(pixelLoc[2] - pixelLoc[3]));
}
