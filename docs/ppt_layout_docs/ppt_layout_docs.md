# 1. PPT Layout 설계

부산항 정기노선도 PPT 자동화를 위한 Layout 및 자동화 대상을 설계하는 문서

작성일 : 2025.10.01.

Update : 2025.10.01.

Update Release

[2025.10.01.] 문서 생성 및 PPT Layout 설계

1. **PPT Layout**
    1. **Layout Figure**
        
        ![image.png](image.png)
        
        ![image.png](image%201.png)
        
    2. **Layout Spec.**
        
        
        | No | ElementClass | ElementLevel | ElementName | ElementDetail | Width(cm) | Height(cm) | ElementColor | FontColor | FontSize | FontStyle | FontAlign | FontType |
        | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
        | 1 | box | service_name | box_region | {Rno}_{Region} | 7.5 | 2.5 | 0/51/153 | white | 28 | bold | middle | Arial |
        | 2 | box | service_name | box_service_name | {[Carriers]} {ServiceName} | 24 | 2.5 | 230/238/240 | black | 20 | bold | middle | Arial |
        | 3 | tbl | service_info | tbl_service_info |  | 24.3 | 3 |  |  |  |  |  |  |
        | 4 | tbl | service_info | tbl_carriers_header | Carriers | 5.5 | 0.7 | 0/32/96 | white | 14 | bold | middle | Arial |
        | 5 | tbl | service_info | tbl_duration_header | Dur. | 1.3 | 0.7 | 0/32/96 | white | 14 | bold | middle | Arial |
        | 6 | tbl | service_info | tbl_frequency_header | Freq. | 1.3 | 0.7 | 0/32/96 | white | 14 | bold | middle | Arial |
        | 7 | tbl | service_info | tbl_ships_header | Ships | 3.1 | 0.7 | 0/32/96 | white | 14 | bold | middle | Arial |
        | 8 | tbl | service_info | tbl_rotation_header | Rotation | 13.1 | 0.7 | 0/32/96 | white | 14 | bold | middle | Arial |
        | 9 | tbl | service_info | tbl_carriers | {Carriers} | 5.5 | 2.3 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 10 | tbl | service_info | tbl_duration | {Dur} | 1.3 | 2.3 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 11 | tbl | service_info | tbl_frequency | {Freq} | 1.3 | 2.3 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 12 | tbl | service_info | tbl_ships | {Ships} | 3.1 | 2.3 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 13 | tbl | service_info | tbl_rotation | {PortRotation} | 13.1 | 2.3 | 0/0/0 | black | 12 | bold | left | Arial |
        | 14 | tbl | proforma | tbl_proforma_1 |  | 6.4 | 2.9 |  |  |  |  |  |  |
        | 15 | tbl | proforma | tbl_proforma_2 |  | 6.4 | 2.9 |  |  |  |  |  |  |
        | 16 | tbl | proforma | tbl_proforma_3 |  | 6.4 | 2.9 |  |  |  |  |  |  |
        | 17 | tbl | proforma | tbl_terminal | Terminal | 2.8 | 0.8 | 0/37/112 | white | 12 | bold | middle | Arial |
        | 18 | tbl | proforma | tbl_wtp | Weekly throughput | 2.8 | 1.3 | 0/37/112 | white | 12 | bold | middle | Arial |
        | 19 | tbl | proforma | tbl_sch | Schedule | 2.8 | 0.8 | 0/37/112 | white | 12 | bold | middle | Arial |
        | 20 | tbl | proforma | tbl_terminal_1 | {T1Name} | 3.6 | 0.8 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 21 | tbl | proforma | tbl_wtp_1 | {T1Wtp} | 3.6 | 1.3 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 22 | tbl | proforma | tbl_sch_1 | {T1Sch} | 3.6 | 0.8 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 23 | tbl | proforma | tbl_terminal_2 | {T2Name} | 3.6 | 0.8 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 24 | tbl | proforma | tbl_wtp_2 | {T2Wtp} | 3.6 | 1.3 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 25 | tbl | proforma | tbl_sch_2 | {T2Sch} | 3.6 | 0.8 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 26 | tbl | proforma | tbl_terminal_3 | {T3Name} | 3.6 | 0.8 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 27 | tbl | proforma | tbl_wtp_3 | {T3Wtp} | 3.6 | 1.3 | 0/0/0 | black | 12 | bold | middle | Arial |
        | 28 | tbl | proforma | tbl_sch_3 | {T3Sch} | 3.6 | 0.8 | 0/0/0 | black | 12 | bold | middle | Arial |