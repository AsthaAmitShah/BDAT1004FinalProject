import { Component, OnInit } from '@angular/core';
import { ApiService } from './api.service';
import * as Highcharts from 'highcharts';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit{
  
  Highcharts: typeof Highcharts = Highcharts;
  chartData: any; 
    constructor(private apiSvc:ApiService) {
    
  } 
  ngOnInit(): void {
    this.apiSvc.onChartDataReady.subscribe(
      (chartData) => {
        this.chartData = chartData;
      }
    );
    this.apiSvc.initializeData();
  }
  title = 'dataProgrammingDashboard';
}
