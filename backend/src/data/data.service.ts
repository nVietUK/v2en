import { Injectable } from '@nestjs/common';
import { Data } from './data.entity';
import { NewDataInput } from './dto/data.args';
import { FindOptionsWhere } from 'typeorm';
import { DataRepository } from './data.repository';

@Injectable()
export class DataService {
	constructor(private dataRepository: DataRepository) {}

	findAll(): Promise<Data[]> {
		return this.dataRepository.find();
	}

	findOneBy(where: FindOptionsWhere<Data>): Promise<Data> {
		return this.dataRepository.findOneBy(where);
	}

	async remove(id: number): Promise<void> {
		await this.dataRepository.delete(id);
	}

	async create(newDataInput: NewDataInput): Promise<Data> {
		return await this.dataRepository.create(newDataInput);
	}
}
