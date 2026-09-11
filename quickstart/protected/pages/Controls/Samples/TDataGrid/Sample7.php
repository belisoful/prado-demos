<?php

class Sample7 extends TPage
{
	protected function getData()
	{
		return [
			['id' => 'ITN001', 'name' => 'Motherboard', 'quantity' => 1, 'price' => 100.00],
			['id' => 'ITN003', 'name' => 'Harddrive', 'quantity' => 2, 'price' => 80.00],
			['id' => 'ITN006', 'name' => 'Keyboard', 'quantity' => 8, 'price' => 20.00],
			['id' => 'ITN012', 'name' => 'Floppy drive', 'quantity' => 50, 'price' => 12.00],
			['id' => 'ITN015', 'name' => 'Mouse pad', 'quantity' => 30, 'price' => 5.00],
		];
	}

	public function onLoad($param)
	{
		parent::onLoad($param);
		if (!$this->IsPostBack) {
			$this->DataGrid->DataSource = $this->Data;
			$this->DataGrid->dataBind();
		}
	}
}
