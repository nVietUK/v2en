import { Body, Controller, Post, Get, Param, Delete } from '@nestjs/common';
import { DataService } from './data.service';
import { Data } from './data.entity';
import { NewDataInput } from './dto/data.args';
import { FindOptionsWhere } from 'typeorm';

@Controller('data')
export class DataController {
	constructor(private readonly dataService: DataService) {}
	@Post()
	create(@Body() newDataInput: NewDataInput): Promise<Data> {
		return this.dataService.create(newDataInput);
	}

	@Get()
	findAll(): Promise<Data[]> {
		return this.dataService.findAll();
	}

	@Get(':id')
	findOneBy(@Param('args') args: FindOptionsWhere<Data>): Promise<Data> {
		return this.dataService.findOneBy(args);
	}

	@Delete(':id')
	remove(@Param('id') id: number): Promise<void> {
		return this.dataService.remove(id);
	}
}
