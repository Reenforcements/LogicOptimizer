module Test1(
    input [15:0]A,
    input [15:0]B,
    output reg C
);

reg [15:0]temp;
always @ (*) begin
	temp = A * B;
    C = temp[0] 
		^ temp[1]
		& temp[2]
		| temp[3]
		| temp[4]
		& temp[5]
		| temp[6]
		^ temp[7]
		^ temp[8]
		& temp[9]
		| temp[10]
		| temp[11]
		| temp[12]
		| temp[13]
		& temp[14]
		& temp[15];
end

endmodule
