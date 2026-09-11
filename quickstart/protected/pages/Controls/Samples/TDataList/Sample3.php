<?php

class Sample3 extends TPage
{
	protected function getData()
	{
		return [
			['id' => 'ITN001', 'name' => 'Motherboard', 'quantity' => 1, 'price' => 100.00, 'imported' => true],
			['id' => 'ITN002', 'name' => 'CPU', 'quantity' => 1, 'price' => 150.00, 'imported' => true],
			['id' => 'ITN003', 'name' => 'Harddrive', 'quantity' => 2, 'price' => 80.00, 'imported' => false],
			['id' => 'ITN004', 'name' => 'Sound card', 'quantity' => 1, 'price' => 40.00, 'imported' => false],
		];
	}

	public function onLoad($param)
	{
		parent::onLoad($param);
		if (!$this->IsPostBack) {
			$this->DataList->DataSource = $this->Data;
			$this->DataList->dataBind();
		}
	}

	public function selectItem($sender, $param)
	{
		$key = $this->DataList->DataKeys[$this->DataList->SelectedItemIndex];
		$this->Result->Text = 'You selected item ' . $key . '.';
	}
}
