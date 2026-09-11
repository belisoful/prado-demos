<com:TPanel
	BackColor=<%# $this->ItemIndex % 2 ? '#E6ECFF' : '#BFCFFF' %>
	Style="padding:6px; margin-bottom:2px">
	<strong><com:TLabel Text=<%# $this->Data['name'] %> /></strong>
	(<com:TLabel Text=<%# $this->Data['id'] %> />)
	&mdash;
	<com:TLabel Text=<%# $this->OriginLabel %> />
	<div>
		<com:TLabel Text=<%# $this->Data['quantity'] %> />
		&times; $<com:TLabel Text=<%# $this->Data['price'] %> />
		= $<com:TLabel Text=<%# $this->Subtotal %> />
	</div>
	<com:TLinkButton Text="Select this item" CommandName="select" />
</com:TPanel>
