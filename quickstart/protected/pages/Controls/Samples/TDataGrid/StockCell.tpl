<com:TLabel
	Text=<%# $this->Data['quantity'] . ' in stock (' . $this->StockLevel . ')' %>
	ForeColor=<%# $this->StockColor %>
	Font.Bold=<%# $this->StockLevel === 'critical' %> />
