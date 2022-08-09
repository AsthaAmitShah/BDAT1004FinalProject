import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  chartData: any;
  onChartDataReady: Subject<any> = new Subject();


  constructor(private http: HttpClient) {  }
  
  initializeData(){
    this.http.get("https://open.er-api.com/v6/latest/USD").subscribe(
      (data:any) => {
        this.transformData(data);
      }
    );

    //
  }

  private transformData(apiData: any) {
    const categories: Array<string> = [];
    const data: Array<number> = [];
    for (const key in apiData.rates) {
      categories.push(key);
      data.push(apiData.rates[key as keyof object]);
    }
   
    const chartData =
    {
      "chart": {
        "type": "bar"
      },
      "title": {
        "text": "Currency"
      },
      "subtitle": {
        "text": "Source: https://open.er-api.com/v6/latest/USD"
      },
      "xAxis": {
        "categories": categories,
        "crosshair": true
      },
      "yAxis": {
        "min": 0,
        "title": {
          "text": "USD"
        }
      },
      "tooltip": {
        "headerFormat": "<span style=\"font-size:10px\">{point.key}</span><table>",
        "pointFormat": "<tr><td style=\"color:{series.color};padding:0\">{series.name}: </td><td style=\"padding:0\"><b>{point.y:.1f} mm</b></td></tr>",
        "footerFormat": "</table>",
        "shared": true,
        "useHTML": true
      },
      "plotOptions": {
        "column": {
          "pointPadding": 0.2,
          "borderWidth": 0
        }
      },
      "series": [
        {
          "name": "USD",
          "data": data
        }
      ]
    }
    this.onChartDataReady.next(chartData);
  }
    
  }

