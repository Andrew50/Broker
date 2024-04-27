import { chart } from './class.js';   

import { request } from '../store.js';

chart.prototype.updateData = function(chart_data) {
    this.data = chart_data;
    this.draw();
}

chart.prototype.checkData = function() {
    if (this.dataOffCooldown) {
        const distFromEnd = (this.data.length + this.a - Math.floor((this.pixelBounds.right) / this.candleWidth))*this.candleWidth;
        if (distFromEnd < 700) {
            const loadNum = Math.floor(1500 / Math.sqrt(this.candleWidth));
            this.updateData(loadNum,false);
        }
    }

}

chart.prototype.updateQuery = function(ticker, i, t,pm) {
    if (this.ticker != ticker || this.i != i || this.nextT != t || this.pm != pm) {
        this.ticker = ticker;
        this.i = i;
        this.nextT = t;
        this.data = [];
        this.updateData(300,true);
    }
}

chart.prototype.updateData = function(bars,newQuery=false) {
    this.dataOffCooldown = false;
    request(null, true, "getChart", this.ticker, this.i, this.nextT, bars).then(val => {
        let [data,err] = val;
        if (err || data == null) {
            if (newQuery) {
                this.data = [];
                this.draw();
                this.queryValid = false;
            }else{
                console.log("no more data to load");
            }
            return;
        }
        data = data.reverse()
        if (newQuery) {
            this.data = data;
        } else {
            console.log("new", data[0][0],data[data.length-1][0],"old",this.data[0][0],this.data[this.data.length-1][0]);
            this.data = [ ...data,...this.data];
        }
        this.nextT = data[0][0];
        this.queryValid = true;
        setTimeout(() => {
            this.dataOffCooldown = true;
        }, this.dataRateLimit);
        if (newQuery) {
            this.draw();
        }
    });
}

