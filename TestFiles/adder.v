module Test1(
    input [7:0]A,
    input [7:0]B,
    output reg C
);

reg [7:0]temp;
always @ (*) begin
	temp = A + B;
    C = temp[0] ^ temp[1] | temp[2] & temp[3] & temp[4] | temp[5] | temp[6] | temp[7];
end

endmodule
