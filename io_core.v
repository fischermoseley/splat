/* Generated by Yosys 0.27+22 (git sha1 53c0a6b78, aarch64-apple-darwin20.2-clang 10.0.0-4ubuntu1 -fPIC -Os) */

module top(data_i, rw_i, valid_i, addr_o, data_o, rw_o, valid_o, probe0, probe1, probe2, probe3, probe4, probe5, probe6, probe7, probe0_buf, probe1_buf, probe2_buf, probe3_buf, probe4_buf, probe5_buf
, probe6_buf, probe7_buf, clk, rst, addr_i);
  reg \$auto$verilog_backend.cc:2097:dump_module$1  = 0;
  wire \$1 ;
  wire [15:0] \$11 ;
  wire [15:0] \$13 ;
  wire [15:0] \$15 ;
  wire [15:0] \$17 ;
  wire [15:0] \$19 ;
  wire [15:0] \$21 ;
  wire [15:0] \$23 ;
  wire [15:0] \$25 ;
  wire [15:0] \$27 ;
  wire [15:0] \$29 ;
  wire \$3 ;
  wire \$31 ;
  wire \$33 ;
  wire \$35 ;
  wire [16:0] \$37 ;
  wire \$39 ;
  wire \$41 ;
  wire \$43 ;
  wire [16:0] \$45 ;
  wire \$47 ;
  wire \$49 ;
  wire \$5 ;
  wire \$51 ;
  wire [16:0] \$53 ;
  wire \$55 ;
  wire \$57 ;
  wire \$59 ;
  wire [16:0] \$61 ;
  wire \$63 ;
  wire \$65 ;
  wire \$67 ;
  wire [16:0] \$69 ;
  wire [16:0] \$7 ;
  wire [15:0] \$9 ;
  input [15:0] addr_i;
  wire [15:0] addr_i;
  output [15:0] addr_o;
  reg [15:0] addr_o = 16'h0000;
  reg [15:0] \addr_o$next ;
  input clk;
  wire clk;
  input [15:0] data_i;
  wire [15:0] data_i;
  output [15:0] data_o;
  reg [15:0] data_o = 16'h0000;
  reg [15:0] \data_o$next ;
  input probe0;
  wire probe0;
  output probe0_buf;
  reg probe0_buf = 1'h0;
  reg \probe0_buf$next ;
  input [1:0] probe1;
  wire [1:0] probe1;
  output [1:0] probe1_buf;
  reg [1:0] probe1_buf = 2'h0;
  reg [1:0] \probe1_buf$next ;
  input [7:0] probe2;
  wire [7:0] probe2;
  output [7:0] probe2_buf;
  reg [7:0] probe2_buf = 8'h00;
  reg [7:0] \probe2_buf$next ;
  input [19:0] probe3;
  wire [19:0] probe3;
  output [19:0] probe3_buf;
  reg [19:0] probe3_buf = 20'h00000;
  reg [19:0] \probe3_buf$next ;
  output probe4;
  reg probe4 = 1'h1;
  reg \probe4$next ;
  output probe4_buf;
  reg probe4_buf = 1'h1;
  reg \probe4_buf$next ;
  output [1:0] probe5;
  reg [1:0] probe5 = 2'h3;
  reg [1:0] \probe5$next ;
  output [1:0] probe5_buf;
  reg [1:0] probe5_buf = 2'h3;
  reg [1:0] \probe5_buf$next ;
  output [7:0] probe6;
  reg [7:0] probe6 = 8'h06;
  reg [7:0] \probe6$next ;
  output [7:0] probe6_buf;
  reg [7:0] probe6_buf = 8'h06;
  reg [7:0] \probe6_buf$next ;
  output [19:0] probe7;
  reg [19:0] probe7 = 20'h00007;
  reg [19:0] \probe7$next ;
  output [19:0] probe7_buf;
  reg [19:0] probe7_buf = 20'h00007;
  reg [19:0] \probe7_buf$next ;
  input rst;
  wire rst;
  input rw_i;
  wire rw_i;
  output rw_o;
  reg rw_o = 1'h0;
  reg \rw_o$next ;
  reg strobe = 1'h0;
  reg \strobe$next ;
  input valid_i;
  wire valid_i;
  output valid_o;
  reg valid_o = 1'h0;
  reg \valid_o$next ;
  assign \$9  = + strobe;
  assign \$11  = + probe0_buf;
  assign \$13  = + probe1_buf;
  assign \$15  = + probe2_buf;
  assign \$17  = + probe3_buf[14:0];
  assign \$1  = addr_i >= 1'h0;
  assign \$19  = + probe3_buf[18:16];
  assign \$21  = + probe4_buf;
  assign \$23  = + probe5_buf;
  assign \$25  = + probe6_buf;
  assign \$27  = + probe7_buf[14:0];
  assign \$29  = + probe7_buf[18:16];
  assign \$31  = addr_i >= 1'h0;
  assign \$33  = addr_o <= 4'ha;
  assign \$35  = \$31  & \$33 ;
  assign \$37  = addr_i - 1'h0;
  assign \$3  = addr_o <= 4'ha;
  assign \$39  = addr_i >= 1'h0;
  assign \$41  = addr_o <= 4'ha;
  assign \$43  = \$39  & \$41 ;
  assign \$45  = addr_i - 1'h0;
  assign \$47  = addr_i >= 1'h0;
  assign \$49  = addr_o <= 4'ha;
  assign \$51  = \$47  & \$49 ;
  assign \$53  = addr_i - 1'h0;
  assign \$55  = addr_i >= 1'h0;
  assign \$57  = addr_o <= 4'ha;
  assign \$5  = \$1  & \$3 ;
  assign \$59  = \$55  & \$57 ;
  assign \$61  = addr_i - 1'h0;
  assign \$63  = addr_i >= 1'h0;
  assign \$65  = addr_o <= 4'ha;
  assign \$67  = \$63  & \$65 ;
  assign \$69  = addr_i - 1'h0;
  always @(posedge clk)
    addr_o <= \addr_o$next ;
  always @(posedge clk)
    data_o <= \data_o$next ;
  always @(posedge clk)
    rw_o <= \rw_o$next ;
  always @(posedge clk)
    valid_o <= \valid_o$next ;
  always @(posedge clk)
    probe0_buf <= \probe0_buf$next ;
  always @(posedge clk)
    probe1_buf <= \probe1_buf$next ;
  always @(posedge clk)
    probe2_buf <= \probe2_buf$next ;
  always @(posedge clk)
    probe3_buf <= \probe3_buf$next ;
  always @(posedge clk)
    probe4 <= \probe4$next ;
  assign \$7  = addr_i - 1'h0;
  always @(posedge clk)
    probe5 <= \probe5$next ;
  always @(posedge clk)
    probe6 <= \probe6$next ;
  always @(posedge clk)
    probe7 <= \probe7$next ;
  always @(posedge clk)
    strobe <= \strobe$next ;
  always @(posedge clk)
    probe4_buf <= \probe4_buf$next ;
  always @(posedge clk)
    probe5_buf <= \probe5_buf$next ;
  always @(posedge clk)
    probe6_buf <= \probe6_buf$next ;
  always @(posedge clk)
    probe7_buf <= \probe7_buf$next ;
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \addr_o$next  = addr_i;
    casez (rst)
      1'h1:
          \addr_o$next  = 16'h0000;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \data_o$next  = data_i;
    casez (\$5 )
      1'h1:
          (* full_case = 32'd1 *)
          casez (rw_i)
            1'h1:
                /* empty */;
            default:
                casez (\$7 )
                  17'h00000:
                      \data_o$next  = \$9 ;
                  17'h00001:
                      \data_o$next  = \$11 ;
                  17'h00002:
                      \data_o$next  = \$13 ;
                  17'h00003:
                      \data_o$next  = \$15 ;
                  17'h00004:
                      \data_o$next  = \$17 ;
                  17'h00005:
                      \data_o$next  = \$19 ;
                  17'h00006:
                      \data_o$next  = \$21 ;
                  17'h00007:
                      \data_o$next  = \$23 ;
                  17'h00008:
                      \data_o$next  = \$25 ;
                  17'h00009:
                      \data_o$next  = \$27 ;
                  17'h0000a:
                      \data_o$next  = \$29 ;
                endcase
          endcase
    endcase
    casez (rst)
      1'h1:
          \data_o$next  = 16'h0000;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe6$next  = probe6;
    casez (strobe)
      1'h1:
          \probe6$next  = probe6_buf;
    endcase
    casez (rst)
      1'h1:
          \probe6$next  = 8'h06;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe7$next  = probe7;
    casez (strobe)
      1'h1:
          \probe7$next  = probe7_buf;
    endcase
    casez (rst)
      1'h1:
          \probe7$next  = 20'h00007;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \strobe$next  = strobe;
    casez (\$35 )
      1'h1:
          casez (rw_i)
            1'h1:
                casez (\$37 )
                  17'h00000:
                      \strobe$next  = data_i[0];
                endcase
          endcase
    endcase
    casez (rst)
      1'h1:
          \strobe$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe4_buf$next  = probe4_buf;
    casez (\$43 )
      1'h1:
          casez (rw_i)
            1'h1:
                casez (\$45 )
                  17'h00000:
                      /* empty */;
                  17'h00006:
                      \probe4_buf$next  = data_i[0];
                endcase
          endcase
    endcase
    casez (rst)
      1'h1:
          \probe4_buf$next  = 1'h1;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe5_buf$next  = probe5_buf;
    casez (\$51 )
      1'h1:
          casez (rw_i)
            1'h1:
                casez (\$53 )
                  17'h00000:
                      /* empty */;
                  17'h00006:
                      /* empty */;
                  17'h00007:
                      \probe5_buf$next  = data_i[1:0];
                endcase
          endcase
    endcase
    casez (rst)
      1'h1:
          \probe5_buf$next  = 2'h3;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe6_buf$next  = probe6_buf;
    casez (\$59 )
      1'h1:
          casez (rw_i)
            1'h1:
                casez (\$61 )
                  17'h00000:
                      /* empty */;
                  17'h00006:
                      /* empty */;
                  17'h00007:
                      /* empty */;
                  17'h00008:
                      \probe6_buf$next  = data_i[7:0];
                endcase
          endcase
    endcase
    casez (rst)
      1'h1:
          \probe6_buf$next  = 8'h06;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe7_buf$next  = probe7_buf;
    casez (\$67 )
      1'h1:
          casez (rw_i)
            1'h1:
                casez (\$69 )
                  17'h00000:
                      /* empty */;
                  17'h00006:
                      /* empty */;
                  17'h00007:
                      /* empty */;
                  17'h00008:
                      /* empty */;
                  17'h00009:
                      \probe7_buf$next [14:0] = data_i[14:0];
                  17'h0000a:
                      \probe7_buf$next [18:16] = data_i[2:0];
                endcase
          endcase
    endcase
    casez (rst)
      1'h1:
          \probe7_buf$next  = 20'h00007;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \rw_o$next  = rw_i;
    casez (rst)
      1'h1:
          \rw_o$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \valid_o$next  = valid_i;
    casez (rst)
      1'h1:
          \valid_o$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe0_buf$next  = probe0_buf;
    casez (strobe)
      1'h1:
          \probe0_buf$next  = probe0;
    endcase
    casez (rst)
      1'h1:
          \probe0_buf$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe1_buf$next  = probe1_buf;
    casez (strobe)
      1'h1:
          \probe1_buf$next  = probe1;
    endcase
    casez (rst)
      1'h1:
          \probe1_buf$next  = 2'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe2_buf$next  = probe2_buf;
    casez (strobe)
      1'h1:
          \probe2_buf$next  = probe2;
    endcase
    casez (rst)
      1'h1:
          \probe2_buf$next  = 8'h00;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe3_buf$next  = probe3_buf;
    casez (strobe)
      1'h1:
          \probe3_buf$next  = probe3;
    endcase
    casez (rst)
      1'h1:
          \probe3_buf$next  = 20'h00000;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe4$next  = probe4;
    casez (strobe)
      1'h1:
          \probe4$next  = probe4_buf;
    endcase
    casez (rst)
      1'h1:
          \probe4$next  = 1'h1;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$1 ) begin end
    \probe5$next  = probe5;
    casez (strobe)
      1'h1:
          \probe5$next  = probe5_buf;
    endcase
    casez (rst)
      1'h1:
          \probe5$next  = 2'h3;
    endcase
  end
endmodule
