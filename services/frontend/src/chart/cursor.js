import { chart } from './class.js';
import { math } from './math.js';
import { toDT } from '../store.js';

chart.prototype.drawCursor = function(){
    this.ctx.save();
    this.ctx.strokeStyle = 'white';
    const xOffset = Math.abs(this.a - Math.floor(this.a)) * this.candleWidth;
    const roundCandle = Math.round(math.remap(this.pixelBounds.left, this.pixelBounds.right, this.dataBounds.left, this.dataBounds.right, this.cursorPos.x - this.candleWidth/2 + xOffset));
    const roundCandlePos = math.remap(this.dataBounds.left, this.dataBounds.right, this.pixelBounds.left, this.pixelBounds.right, roundCandle);
    const price = math.remap(this.pixelBounds.topC, this.pixelBounds.bottomC, this.dataBounds.top, this.dataBounds.bottom, this.cursorPos.y);
    this.ctx.beginPath();
    this.ctx.moveTo(this.pixelBounds.left, this.cursorPos.y);
    this.ctx.lineTo(this.canvas.width - this.margin, this.cursorPos.y);
    this.ctx.stroke();
    this.ctx.beginPath();
    this.ctx.moveTo(roundCandlePos - xOffset + this.candleWidth / 2 , this.pixelBounds.bottom);
    this.ctx.lineTo(roundCandlePos - xOffset + this.candleWidth / 2 , this.pixelBounds.top);
    this.ctx.stroke();
    this.ctx.restore();
    this.ctx.clearRect(this.canvas.width - this.margin, this.cursorPos.y - 6, this.margin, 12);
    this.drawCursorText(math.sigFigs(price, 3), [this.canvas.width - 2, this.cursorPos.y], this.margin * 0.5);
    //aj bs
    //console.log(this.a + xOffset - (this.cursorPos.x/this.candleWidth));
    const index = Math.round(this.a - (this.dataBounds.right - roundCandle) + 1);
    //console.log(this.dataBounds.left, this.dataBounds.right);
    this.currentPrice = price;
    this.currentT = this.data[this.data.length + index][0];
    let arbOffset;
    let arg;
    if (this.isIntraday()) {
        arg = 2;
        arbOffset = 80;
    }else{
        arg = 1;
        arbOffset = 42;
    }

    this.drawCursorText(toDT(this.currentT,arg), [arbOffset + roundCandlePos - xOffset - this.wickWidth / 2, this.pixelBounds.bottom + this.margin / 2], this.margin * 0.5); 
}

chart.prototype.isIntraday = function(){
    return !(this.i.includes('d') || this.i.includes('w') || this.i.includes('m'));
}

chart.prototype.drawCursorText = function(text, loc, size) {
    const ctx = this.ctx;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.font = "bold " + size + "px Courier";
    // Measure the text
    const metrics = ctx.measureText(text);
    const textWidth = metrics.width;
    const textHeight = size; // Approximation based on font size
    // Calculate the rectangle's position and size
    const rectX = loc[0] - textWidth;
    const rectY = loc[1] - textHeight / 2;
    const rectWidth = textWidth;
    const rectHeight = textHeight;
    // Draw the rectangle with a solid color
    ctx.fillStyle = 'grey'; // Color for the background, can be changed to any color
    ctx.fillRect(rectX, rectY, rectWidth, rectHeight);
    // Set fillStyle for text and draw the text
    ctx.fillStyle = 'white';
    ctx.fillText(text, ...loc);
}
